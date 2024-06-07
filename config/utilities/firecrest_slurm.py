# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import functools
import hostlist
import itertools
import logging
import os
import re
import shutil
import stat
import sys
import time
from packaging.version import Version

import reframe.core.runtime as rt
import reframe.core.schedulers as sched
from reframe.core.backends import register_scheduler
from reframe.core.schedulers.slurm import (SlurmJobScheduler,
                                           slurm_state_completed,
                                           _SlurmNode)
from reframe.core.exceptions import JobSchedulerError
import reframe.utility.osext as osext

if sys.version_info >= (3, 7):
    import firecrest as fc

_run_strict = functools.partial(osext.run_command, check=True)


def join_and_normalize(*args):
    joined_path = os.path.join(*args)
    normalized_path = os.path.normpath(joined_path)
    return normalized_path


class _SlurmFirecrestJob(sched.Job):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_array = False
        self._is_cancelling = False
        self._remotedir = None
        self._localdir = None

        # The compacted nodelist as reported by Slurm. This must be updated
        # in every poll as Slurm may be slow in reporting the exact nodelist
        self._nodespec = None
        self._stage_prefix = rt.runtime().stage_prefix

    @property
    def is_array(self):
        return self._is_array

    @property
    def is_cancelling(self):
        return self._is_cancelling

    @property
    def remotedir(self):
        return self._remotedir

    @property
    def nodelist(self):
        # Generate the nodelist only after the job is finished
        if slurm_state_completed(self.state):
            self._nodelist = hostlist.expand_hostlist(self._nodespec)

        return self._nodelist


@register_scheduler('firecrest-slurm')
class SlurmFirecrestJobScheduler(SlurmJobScheduler):
    def __init__(self, *args, **kwargs):
        def set_mandatory_var(var):
            res = os.environ.get(var)
            if res:
                return res

            raise JobSchedulerError(f'the env var {var} is mandatory for the '
                                    f'firecrest scheduler')

        if sys.version_info < (3, 7):
            raise JobSchedulerError('the firecrest scheduler needs '
                                    'python>=3.7')

        super().__init__(*args, **kwargs)
        client_id = set_mandatory_var('FIRECREST_CLIENT_ID')
        client_secret = set_mandatory_var('FIRECREST_CLIENT_SECRET')
        token_uri = set_mandatory_var('AUTH_TOKEN_URL')
        firecrest_url = set_mandatory_var('FIRECREST_URL')
        self._system_name = set_mandatory_var('FIRECREST_SYSTEM')
        self._remotedir_prefix = set_mandatory_var('FIRECREST_BASEDIR')
        # FIXME: This is not mandatory, but it is recommended to set until
        # FirecREST v1.16.0 is available in all systems
        self._firecrest_api_version = Version(
            os.environ.get(
                'FIRECREST_API_VERSION',
                default='1.15.0'
            )
        )

        # Setup the client for the specific account
        self.client = fc.Firecrest(
            firecrest_url=firecrest_url,
            authorization=fc.ClientCredentialsAuth(client_id, client_secret,
                                                   token_uri)
        )

        params = self.client.parameters()
        for p in params['utilities']:
            if p['name'] == 'UTILITIES_MAX_FILE_SIZE':
                self._max_file_size_utilities = float(p['value'])*1000000
                break

        self._local_filetimestamps = {}
        self._remote_filetimestamps = {}
        self._cleaned_remotedirs = set()

    def make_job(self, *args, **kwargs):
        return _SlurmFirecrestJob(*args, **kwargs)

    def _push_compressed_artefacts(self, job):
        def _extract(archive_path, dir_path):
            intervals = itertools.cycle([1, 2, 3])
            try:
                original_level = logging.getLogger().level
                logging.getLogger().setLevel(100)
                self.client.extract(
                    self._system_name,
                    archive_path,
                    dir_path
                )
            except fc.FirecrestException as e:
                # Revert the global logger level back to its original
                # state
                logging.getLogger().setLevel(original_level)
                timeout_str = 'Command has finished with timeout signal'
                # This command has a timeout so it may fail
                if (
                    e.responses[-1].status_code == 400 and
                    e.responses[-1].json().get('error', '') != timeout_str
                ):
                    raise e

                self.log('The directory is too big to extract directly, '
                         'will try with a job... It may time some time.')

                extract_job = self.client.submit_extract_job(
                    self._system_name,
                    archive_path,
                    dir_path
                )
                jobid = extract_job['jobid']
                active_jobs = self.client.poll(
                    self._system_name,
                    [jobid]
                )
                self.log(f'Extract job ID {jobid})')
                while (
                    active_jobs and
                    not slurm_state_completed(active_jobs[0]['state'])
                ):
                    self.log(f"Extract job (jobid={jobid}) with state: "
                             f"{active_jobs[0]['state']}")
                    time.sleep(next(intervals))
                    active_jobs = self.client.poll_active(
                        self._system_name,
                        [jobid]
                    )

                if (
                    active_jobs and
                    active_jobs[0]['state'] != 'COMPLETED'
                ):
                    raise JobSchedulerError(
                        f"extract job (jobid={jobid}) finished with"
                        f"state {active_jobs[0]['state']}"
                    )

                err_output = self.client.head(
                    self._system_name,
                    extract_job['job_file_err']
                )
                if (err_output != ''):
                    raise JobSchedulerError(
                        f'extract job has failed: {err_output}'
                    )
            finally:
                # Always revert the global logger level back to its original
                # state
                logging.getLogger().setLevel(original_level)

        # Compress locally the files
        self.log('Compressing local stage directory')
        local_path = shutil.make_archive(
            base_name='stage_dir_archive_push',
            format='gztar',
            root_dir='.',
            base_dir='.',
        )

        # Upload
        remote_path = job._remotedir
        f_size = os.path.getsize(local_path)
        remote_file_path = os.path.join(
            remote_path,
            os.path.basename(local_path)
        )
        if f_size <= self._max_file_size_utilities:
            self.client.simple_upload(
                self._system_name,
                local_path,
                remote_path
            )
        else:
            self.log(
                f'Archive file is {f_size} bytes, so it may take some time...'
            )
            up_obj = self.client.external_upload(
                self._system_name,
                local_path,
                remote_path
            )
            up_obj.finish_upload()
            sleep_time = itertools.cycle([1, 5, 10])
            while up_obj.in_progress:
                t = next(sleep_time)
                self.log(
                    f'Archive is not yet in the filesystem, will sleep '
                    f'for {t} sec'
                )
                time.sleep(t)

        # Extract stagedir
        self.log(f'Extracting {remote_file_path} to {remote_path}')
        _extract(
            remote_file_path,
            remote_path
        )

        # Remove the archives
        self.log('Removing local and remote archives')
        os.remove(local_path)
        self.client.simple_delete(self._system_name, remote_file_path)

    def _push_artefacts(self, job):
        def _setup_permissions(local_file_path, remote_file_path):
            permissions = oct(os.lstat(local_file_path)[stat.ST_MODE])[-3:]
            self.client.chmod(
                self._system_name,
                remote_file_path,
                permissions
            )

        def _upload(local_path, remote_path):
            f_size = os.path.getsize(local_path)
            remote_file_path = os.path.join(
                remote_path,
                os.path.basename(local_path)
            )
            if f_size <= self._max_file_size_utilities:
                self.client.simple_upload(
                    self._system_name,
                    local_path,
                    remote_path
                )
                _setup_permissions(local_path, remote_file_path)
                return None
            else:
                self.log(
                    f'File {f} is {f_size} bytes, so it may take some time...'
                )
                up_obj = self.client.external_upload(
                    self._system_name,
                    local_path,
                    remote_path
                )
                up_obj.finish_upload()
                # We will set up the permission after the files are available
                # on the remote filesystem
                return (up_obj, local_path, remote_file_path)

        for dirpath, dirnames, filenames in os.walk('.'):
            for d in dirnames:
                new_dir = join_and_normalize(job._remotedir, dirpath, d)
                self.log(f'Creating remote directory {new_dir}')
                self.client.mkdir(self._system_name, new_dir, p=True)

            async_uploads = []
            remote_dir_path = join_and_normalize(job._remotedir, dirpath)
            for f in filenames:
                local_norm_path = join_and_normalize(
                    job._localdir, dirpath, f
                )
                modtime = os.path.getmtime(local_norm_path)
                last_modtime = self._local_filetimestamps.get(local_norm_path)
                if (last_modtime != modtime):
                    self._local_filetimestamps[local_norm_path] = modtime
                    self.log(
                        f'Uploading file {f} in {remote_dir_path}'
                    )
                    up = _upload(
                        local_norm_path,
                        remote_dir_path
                    )
                    if up:
                        async_uploads.append(up)

            sleep_time = itertools.cycle([1, 5, 10])
            while async_uploads:
                still_uploading = []
                for up_obj, local_file_path, remote_file_path in async_uploads:
                    upload_status = int(up_obj.status)
                    if upload_status < 114:
                        still_uploading.append(
                            (up_obj, local_file_path, remote_file_path)
                        )
                        self.log(f'file is still uploading, '
                                 f'status: {upload_status}')
                    elif upload_status > 114:
                        raise JobSchedulerError(
                            'could not upload file to remote staging '
                            'area'
                        )
                    else:
                        _setup_permissions(local_file_path, remote_file_path)

                async_uploads = still_uploading
                t = next(sleep_time)
                self.log(
                    f'Waiting for the uploads, sleeping for {t} sec'
                )
                time.sleep(t)

            # Update timestamps for remote directory
            remote_files = self.client.list_files(
                self._system_name,
                remote_dir_path,
                show_hidden=True
            )
            for f in remote_files:
                local_norm_path = join_and_normalize(remote_dir_path,
                                                     f['name'])
                self._remote_filetimestamps[local_norm_path] = (
                    f['last_modified']
                )

    def _pull_compressed_artefacts(self, job):
        def _compress(dir_path, archive_path):
            intervals = itertools.cycle([1, 2, 3])
            try:
                original_level = logging.getLogger().level
                logging.getLogger().setLevel(100)
                self.client.compress(
                    self._system_name,
                    dir_path,
                    archive_path
                )
            except fc.FirecrestException as e:
                logging.getLogger().setLevel(original_level)
                timeout_str = 'Command has finished with timeout signal'
                # This command has a timeout so it may fail
                if (
                    e.responses[-1].status_code == 400 and
                    e.responses[-1].json().get('error', '') != timeout_str
                ):
                    raise e

                self.log('The directory is too big to compress directly, '
                         'will try with a job... It may time some time.')

                compression_job = self.client.submit_compress_job(
                    self._system_name,
                    dir_path,
                    archive_path
                )
                jobid = compression_job['jobid']
                active_jobs = self.client.poll(
                    self._system_name,
                    [jobid]
                )
                self.log(f'Compression job ID: {jobid}')
                while (
                    active_jobs and
                    not slurm_state_completed(active_jobs[0]['state'])
                ):
                    time.sleep(next(intervals))
                    active_jobs = self.client.poll_active(
                        self._system_name,
                        [jobid]
                    )

                if (
                    active_jobs and
                    active_jobs[0]['state'] != 'COMPLETED'
                ):
                    raise JobSchedulerError(
                        f"compression job (jobid={jobid}) finished with"
                        f"state {active_jobs[0]['state']}"
                    )

                err_output = self.client.head(
                    self._system_name,
                    compression_job['job_file_err']
                )
                if (err_output != ''):
                    raise JobSchedulerError(
                        'compression job has failed: {err_output}'
                    )
            finally:
                # Always revert the global logger level back to its original
                # state
                logging.getLogger().setLevel(original_level)

        def _download(remote_path, local_path, f_size):
            if f_size <= self._max_file_size_utilities:
                self.client.simple_download(
                    self._system_name,
                    remote_path,
                    local_path
                )
            else:
                self.log(
                    f'File {remote_path} is {f_size} bytes, so it may take '
                    f'some time...'
                )
                up_obj = self.client.external_download(
                    self._system_name,
                    remote_path
                )
                up_obj.finish_download(local_path)
                return up_obj

        # Compress remote files
        self.log('Compressing remote stage directory')
        remote_achive_path = os.path.join(
            self._remotedir_prefix,
            'stage_dir_archive_pull.tar.gz'
        )
        _compress(
            job._remotedir,
            remote_achive_path
        )

        # Download the remote directory
        file_size = self.client.stat(
            self._system_name,
            remote_achive_path
        )['size']
        local_archive_path = os.path.join(
            os.path.dirname(job._localdir),
            'stage_dir_archive_pull.tar.gz'
        )
        self.log(f'Downloading file {remote_achive_path} in {job._localdir}')
        _download(
            remote_achive_path,
            local_archive_path,
            file_size
        )

        # Extract the files locally
        self.log(f'Extracting {local_archive_path} to {job._localdir}')
        cmd = (
            f'tar -xzf {local_archive_path} -C '
            f'{os.path.dirname(job._localdir)}'
        )
        _run_strict(cmd)

        # Remove the remote and local archives
        self.log('Removing local and remote archives')
        os.remove(local_archive_path)
        self.client.simple_delete(self._system_name, remote_achive_path)

    def _pull_artefacts(self, job):
        def firecrest_walk(directory):
            contents = self.client.list_files(self._system_name, directory)

            dirs = []
            nondirs = []

            for item in contents:
                if item['type'] == 'd':
                    dirs.append(item['name'])
                else:
                    nondirs.append((item['name'],
                                    item['last_modified'],
                                    int(item['size'])))

            yield directory, dirs, nondirs

            for item in dirs:
                item_path = f'{directory}/{item}'
                yield from firecrest_walk(item_path)

        def _download(remote_path, local_path, f_size):
            if f_size <= self._max_file_size_utilities:
                self.client.simple_download(
                    self._system_name,
                    remote_path,
                    local_path
                )
            else:
                self.log(
                    f'File {f} is {f_size} bytes, so it may take some time...'
                )
                up_obj = self.client.external_download(
                    self._system_name,
                    remote_path
                )
                up_obj.finish_download(local_path)

        if job.name == 'rfm-detect-job':
            # We only need the topo.json file and the job's
            # output and error files
            for file_name in ('rfm-detect-job.out',
                              'rfm-detect-job.err',
                              'topo.json'):

                remote_file_path = os.path.join(
                    job._remotedir,
                    file_name
                )
                local_file_path = os.path.join(
                    job._localdir,
                    file_name
                )
                self.log(f'Downloading file {file_name} in {job._localdir}')
                _download(
                    remote_file_path,
                    local_file_path,
                    0  # these files shoult be small enough for simple_download
                )

            return

        for dirpath, dirnames, files in firecrest_walk(job._remotedir):
            local_dirpath = join_and_normalize(
                job._localdir,
                os.path.relpath(
                    dirpath,
                    job._remotedir
                )
            )
            for d in dirnames:
                new_dir = join_and_normalize(local_dirpath, d)
                self.log(f'Creating local directory {new_dir}')
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)

            for (f, modtime, fsize) in files:
                norm_path = join_and_normalize(dirpath, f)
                local_file_path = join_and_normalize(local_dirpath, f)
                if self._remote_filetimestamps.get(norm_path) != modtime:
                    self.log(f'Downloading file {f} in {local_dirpath}')
                    self._remote_filetimestamps[norm_path] = modtime
                    _download(
                        norm_path,
                        local_file_path,
                        fsize
                    )

                new_modtime = os.path.getmtime(local_file_path)
                self._local_filetimestamps[local_file_path] = new_modtime

    def submit(self, job):
        job._localdir = os.getcwd()
        if job.name == 'rfm-detect-job':
            job._remotedir = os.path.join(
                self._remotedir_prefix,
                os.path.basename(os.getcwd())
            )
        else:
            job._remotedir = os.path.join(
                self._remotedir_prefix,
                os.path.relpath(os.getcwd(), job._stage_prefix)
            )

        if job._remotedir not in self._cleaned_remotedirs:
            # Create clean stage directory in the remote system
            try:
                original_level = logging.getLogger().level
                logging.getLogger().setLevel(100)
                self.client.simple_delete(self._system_name, job._remotedir)
            except fc.HeaderException:
                # The delete request will raise an exception if it doesn't
                # exist, but it can be ignored
                pass
            finally:
                # Always revert the global logger level back to its original
                # state
                logging.getLogger().setLevel(original_level)

            self._cleaned_remotedirs.add(job._remotedir)

        self.client.mkdir(self._system_name, job._remotedir, p=True)
        self.log(f'Creating remote directory {job._remotedir} in '
                 f'{self._system_name}')

        if self._firecrest_api_version <= Version('1.15.0'):
            self._push_artefacts(job)
        else:
            self._push_compressed_artefacts(job)

        intervals = itertools.cycle([1, 2, 3])
        while True:
            try:
                # Make request for submission
                if Version(fc.__version__) >= Version('2.1.0'):
                    submission_result = self.client.submit(
                        self._system_name,
                        script_remote_path=os.path.join(
                            job._remotedir, job.script_filename
                        )
                    )
                else:
                    submission_result = self.client.submit(
                        self._system_name,
                        os.path.join(job._remotedir, job.script_filename),
                        local_file=False
                    )

                break
            except fc.FirecrestException as e:
                stderr = e.responses[-1].json().get('error', '')
                error_match = re.search(
                    rf'({"|".join(self._resubmit_on_errors)})', stderr
                )
                if not self._resubmit_on_errors or not error_match:
                    raise

                t = next(intervals)
                self.log(
                    f'encountered a job submission error: '
                    f'{error_match.group(1)}: will resubmit after {t}s'
                )
                time.sleep(t)

        job._jobid = str(submission_result['jobid'])
        job._submit_time = time.time()

    def allnodes(self):
        if self._firecrest_api_version <= Version('1.16.0'):
            raise NotImplementedError('firecrest slurm backend does not '
                                      'support node listing')

        nodes = set()
        try:
            node_descriptions = self.client.nodes(self._system_name)
        except fc.FirecrestException as e:
            raise JobSchedulerError(
                'could not retrieve node information') from e

        for node_descr in node_descriptions:
            nodes.add(_FirecrestSlurmNode(node_descr))

        return nodes

    def _get_nodes_by_name(self, nodespec):
        nodes = set()
        try:
            node_descriptions = self.client.nodes(
                self._system_name, [nodespec]
            )
        except fc.FirecrestException as e:
            raise JobSchedulerError(
                'could not retrieve node information') from e

        for node_descr in node_descriptions:
            nodes.add(_FirecrestSlurmNode(node_descr))

        return nodes

    def _get_default_partition(self):
        try:
            part_descriptions = self.client.partitions(self._system_name)
        except fc.FirecrestException as e:
            raise JobSchedulerError('could not extract the partitions') from e

        for part in part_descriptions:
            if part['Default'] == 'YES':
                return part['PartitionName']

        return None

    def _get_reservation_nodes(self, reservation):
        try:
            res_descr = self.client.reservations(
                self._system_name, [reservation]
            )[0]
        except (fc.FirecrestException, IndexError) as e:
            raise JobSchedulerError(f"could not extract the node names for "
                                    f"reservation '{reservation}'") from e

        try:
            node_descriptions = self.client.nodes(
                self._system_name, [res_descr['Nodes']]
            )
        except fc.FirecrestException as e:
            raise JobSchedulerError(f"could not extract the node for "
                                    f"reservation '{reservation}'") from e

        nodes = set()
        for node_descr in node_descriptions:
            nodes.add(_FirecrestSlurmNode(node_descr))

        return nodes

    def poll(self, *jobs):
        '''Update the status of the jobs.'''

        if jobs:
            # Filter out non-jobs
            jobs = [job for job in jobs if job is not None]

        if not jobs:
            return

        poll_results = self.client.poll(
            self._system_name, [job.jobid for job in jobs]
        )
        job_info = {}
        for r in poll_results:
            # Take into account both job arrays and heterogeneous jobs
            jobid = re.split(r'_|\+', r['jobid'])[0]
            job_info.setdefault(jobid, []).append(r)

        for job in jobs:
            try:
                jobarr_info = job_info[job.jobid]
            except KeyError:
                continue

            # Join the states with ',' in case of job arrays|heterogeneous
            # jobs
            job._state = ','.join(m['state'] for m in jobarr_info)

            self._cancel_if_pending_too_long(job)
            if slurm_state_completed(job.state):
                # Since Slurm exitcodes are positive take the maximum one
                job._exitcode = max(
                    int(m['exit_code'].split(":")[0]) for m in jobarr_info
                )

            # Use ',' to join nodes to be consistent with Slurm syntax
            job._nodespec = ','.join(m['nodelist'] for m in jobarr_info)

    def wait(self, job):
        if self.finished(job):
            if job.is_array:
                self._merge_files(job)

            if self._firecrest_api_version <= Version('1.15.0'):
                self._pull_artefacts(job)
            else:
                self._pull_compressed_artefacts(job)

            return

        intervals = itertools.cycle([1, 2, 3])
        while not self.finished(job):
            self.poll(job)
            time.sleep(next(intervals))

        if self._firecrest_api_version <= Version('1.15.0'):
            self._pull_artefacts(job)
        else:
            self._pull_compressed_artefacts(job)

        if job.is_array:
            self._merge_files(job)

    def cancel(self, job):
        self.client.cancel(job.system_name, job.jobid)
        job._is_cancelling = True


class _FirecrestSlurmNode(_SlurmNode):
    '''Class representing a Slurm node.'''

    def __init__(self, node_descr):
        self._name = node_descr['NodeName']
        self._partitions = set(node_descr['Partitions'])
        self._active_features = set(node_descr['ActiveFeatures'])
        self._states = set(node_descr['State'])
        self._descr = node_descr
