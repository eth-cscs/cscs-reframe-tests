# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import functools
import hostlist
import itertools
import os
import re
import shutil
import time

import reframe.core.runtime as rt
import reframe.core.schedulers as sched
import reframe.utility.osext as osext
from reframe.core.backends import register_scheduler
from reframe.core.exceptions import JobSchedulerError
from reframe.core.schedulers.slurm import (SlurmJobScheduler,
                                           slurm_state_completed,
                                           _SlurmNode)

import firecrest as fc

_run_strict = functools.partial(osext.run_command, check=True)


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
        if slurm_state_completed(self.state) and self._nodespec:
            self._nodelist = hostlist.expand_hostlist(self._nodespec)

        return self._nodelist


@register_scheduler('firecrest-slurm')
class SlurmFirecrestJobScheduler(SlurmJobScheduler):
    '''Job scheduler for Slurm systems accessed through FirecREST v2.

    The scheduler stages the test artefacts to a remote directory through
    the FirecREST filesystem API, submits the generated script with the
    compute API and pulls back the results when the job finishes.
    '''

    def __init__(self, *args, **kwargs):
        def set_mandatory_var(var):
            res = os.environ.get(var)
            if res:
                return res

            raise JobSchedulerError(f'the env var {var} is mandatory for the '
                                    f'firecrest scheduler')

        super().__init__(*args, **kwargs)
        client_id = set_mandatory_var('FIRECREST_CLIENT_ID')
        client_secret = set_mandatory_var('FIRECREST_CLIENT_SECRET')
        token_uri = set_mandatory_var('AUTH_TOKEN_URL')
        firecrest_url = set_mandatory_var('FIRECREST_URL')
        self._system_name = set_mandatory_var('FIRECREST_SYSTEM')
        self._remotedir_prefix = set_mandatory_var('FIRECREST_BASEDIR')

        # Setup the client for the specific account
        self.client = fc.v2.Firecrest(
            firecrest_url=firecrest_url,
            authorization=fc.ClientCredentialsAuth(client_id, client_secret,
                                                   token_uri)
        )
        api_version = os.environ.get('FIRECREST_API_VERSION')
        if api_version:
            self.client.set_api_version(api_version)

        self._cleaned_remotedirs = set()

    def make_job(self, *args, **kwargs):
        return _SlurmFirecrestJob(*args, **kwargs)

    def _push_artefacts(self, job):
        # Compress the local stage directory; the archive is created in the
        # current working directory, which is the job's stage directory
        self.log('Compressing local stage directory')
        local_archive = shutil.make_archive(
            base_name='stage_dir_archive_push',
            format='gztar',
            root_dir='.',
            base_dir='.',
        )
        archive_name = os.path.basename(local_archive)
        remote_archive = os.path.join(job._remotedir, archive_name)

        # The client will upload directly small files and use the staging
        # area (blocking until the file is on the filesystem) for large ones
        self.log(f'Uploading stage directory archive to {job._remotedir}')
        self.client.upload(
            self._system_name,
            local_archive,
            job._remotedir,
            archive_name
        )

        # The client falls back internally to a transfer job when the
        # extraction takes too long for the api call
        self.log(f'Extracting {remote_archive} to {job._remotedir}')
        self.client.extract(
            self._system_name,
            remote_archive,
            job._remotedir
        )

        self.log('Removing local and remote archives')
        os.remove(local_archive)
        self.client.rm(self._system_name, remote_archive)

    def _pull_artefacts(self, job):
        def _download(remote_path, local_path):
            self.log(f'Downloading file {remote_path} to {local_path}')
            self.client.download(
                self._system_name,
                remote_path,
                local_path
            )

        if job.name == 'rfm-detect-job':
            # We only need the topo.json file and the job's output and
            # error files
            for file_name in ('rfm-detect-job.out',
                              'rfm-detect-job.err',
                              'topo.json'):
                _download(
                    os.path.join(job._remotedir, file_name),
                    os.path.join(job._localdir, file_name)
                )

            return

        # Compress the remote stage directory; the client falls back
        # internally to a transfer job when the compression takes too long
        remote_archive = f'{job._remotedir}_pull.tar.gz'
        self.log(f'Compressing remote stage directory {job._remotedir}')
        self.client.compress(
            self._system_name,
            job._remotedir,
            remote_archive
        )

        local_archive = os.path.join(
            os.path.dirname(job._localdir),
            os.path.basename(remote_archive)
        )
        _download(remote_archive, local_archive)

        # The archive contains the stage directory as its top-level entry,
        # so extract it in the parent directory of the local stage directory
        self.log(f'Extracting {local_archive} to {job._localdir}')
        _run_strict(
            f'tar -xzf {local_archive} -C {os.path.dirname(job._localdir)}'
        )

        self.log('Removing local and remote archives')
        os.remove(local_archive)
        self.client.rm(self._system_name, remote_archive)

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
            # Create a clean stage directory in the remote system
            try:
                self.client.rm(self._system_name, job._remotedir)
            except fc.FirecrestException:
                # The delete request will fail if the directory doesn't
                # exist, but this can be ignored
                pass

            self._cleaned_remotedirs.add(job._remotedir)

        self.log(f'Creating remote directory {job._remotedir} in '
                 f'{self._system_name}')
        self.client.mkdir(self._system_name, job._remotedir,
                          create_parents=True)

        self._push_artefacts(job)

        intervals = itertools.cycle([1, 2, 3])
        while True:
            try:
                submission_result = self.client.submit(
                    self._system_name,
                    working_dir=job._remotedir,
                    script_remote_path=os.path.join(job._remotedir,
                                                    job.script_filename)
                )
                break
            except fc.FirecrestException as e:
                try:
                    stderr = e.responses[-1].json().get('message', '')
                except Exception:
                    stderr = str(e)

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

        job._jobid = str(submission_result['jobId'])
        job._submit_time = time.time()

    def poll(self, *jobs):
        '''Update the status of the jobs.'''

        if jobs:
            # Filter out non-jobs
            jobs = [job for job in jobs if job is not None]

        if not jobs:
            return

        job_info = {}
        for job in jobs:
            try:
                res = self.client.job_info(self._system_name, job.jobid)
            except fc.FirecrestException as e:
                if e.responses[-1].status_code == 404:
                    # The job may not be yet in the scheduler's database
                    continue

                raise JobSchedulerError(
                    'could not retrieve the job information') from e

            if res:
                job_info[job.jobid] = res

        pending_reasons = {}
        for job in jobs:
            try:
                jobarr_info = job_info[job.jobid]
            except KeyError:
                continue

            # Join the states with ',' in case of job arrays|heterogeneous
            # jobs
            job._state = ','.join(self._job_state(m) for m in jobarr_info)

            if slurm_state_completed(job.state):
                # Since Slurm exitcodes are positive take the maximum one
                job._exitcode = max(
                    int(m['status'].get('exitCode') or 0)
                    for m in jobarr_info
                )

            # Use ',' to join nodes to be consistent with Slurm syntax
            job._nodespec = ','.join(m['nodes'] for m in jobarr_info)
            self._update_completion_time(
                job, (m['time'].get('end') for m in jobarr_info)
            )
            reasons = [m['status'].get('stateReason') or ''
                       for m in jobarr_info]
            pending_reasons[job.jobid] = reasons

        # The pending reasons come for free with the job info, so there is
        # no need to throttle the blocked-jobs check as the parent class does
        self._cancel_if_blocked(jobs, pending_reasons)
        self._cancel_if_pending_too_long(jobs)

    def _job_state(self, job_descr):
        state = job_descr['status'].get('state', '')
        if isinstance(state, list):
            state = ','.join(state)

        return state

    def allnodes(self):
        try:
            node_descriptions = self.client.nodes(self._system_name)
        except fc.FirecrestException as e:
            raise JobSchedulerError(
                'could not retrieve node information') from e

        return {_FirecrestSlurmNode(n) for n in node_descriptions}

    def _get_nodes_by_name(self, nodespec):
        requested = set(hostlist.expand_hostlist(nodespec))
        return {n for n in self.allnodes() if n.name in requested}

    def _get_default_partition(self):
        # The FirecREST API does not report the default partition
        return None

    def _get_actual_partition(self, options):
        # We cannot run `srun --test-only` remotely
        return None

    def _get_reservation_nodes(self, reservation):
        try:
            res_descriptions = self.client.reservations(self._system_name)
        except fc.FirecrestException as e:
            raise JobSchedulerError(f"could not extract the nodes for "
                                    f"reservation '{reservation}'") from e

        for res in res_descriptions:
            if res['name'] == reservation:
                res_nodes = set(hostlist.expand_hostlist(res['nodeList']))
                return {n for n in self.allnodes() if n.name in res_nodes}

        raise JobSchedulerError(f"could not find reservation '{reservation}'")

    def wait(self, job):
        intervals = itertools.cycle([1, 2, 3])
        while not self.finished(job):
            self.poll(job)
            time.sleep(next(intervals))

        self._pull_artefacts(job)
        if job.is_array:
            self._merge_files(job)

    def cancel(self, job):
        self.client.cancel_job(self._system_name, job.jobid)
        job._is_cancelling = True

    def cancel_many(self, jobs):
        for job in jobs:
            self.cancel(job)


class _FirecrestSlurmNode(_SlurmNode):
    '''Class representing a Slurm node accessed through FirecREST.'''

    def __init__(self, node_descr):
        self._name = node_descr['name']
        self._partitions = set(node_descr.get('partitions') or [])
        features = node_descr.get('features') or []
        if isinstance(features, str):
            features = features.split(',')

        self._active_features = set(features)
        self._states = set(node_descr.get('state') or [])
        self._descr = node_descr
