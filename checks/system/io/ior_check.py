# Copyright 2016 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import getpass
import os

import reframe as rfm
import reframe.utility.sanity as sn


class fetch_ior_benchmarks(rfm.RunOnlyRegressionTest):
    descr = 'Fetch IOR benchmarks'
    version = variable(str, value='4.0.0')
    executable = 'wget'
    executable_opts = [
        f'https://github.com/hpc/ior/releases/download/{version}/ior-{version}.tar.gz'  # noqa: E501
    ]

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


class build_ior_benchmarks(rfm.CompileOnlyRegressionTest):
    descr = 'Build IOR benchmarks'
    build_system = 'Autotools'
    build_prefix = variable(str)
    ior_benchmarks = fixture(fetch_ior_benchmarks, scope='session')

    # Build on the remote system for consistency
    build_locally = False

    @run_after('init')
    def load_cray_module(self):
        if self.current_system.name in ['eiger', 'pilatus']:
            self.modules = ['cray']

    @run_before('compile')
    def prepare_build(self):
        tarball = f'ior-{self.ior_benchmarks.version}.tar.gz'
        self.build_prefix = tarball[:-7]
        fullpath = os.path.join(self.ior_benchmarks.stagedir, tarball)
        self.prebuild_cmds = [
            f'cp {fullpath} {self.stagedir}',
            f'tar xzf {tarball}',
            f'cd {self.build_prefix}'
        ]

    # FIXME this will not be needed in a ReFrame release including:
    # https://github.com/reframe-hpc/reframe/pull/3157
    @sanity_function
    def validate_build(self):
        return True


class IorCheck(rfm.RunOnlyRegressionTest):
    base_dir = parameter(['/capstor/scratch/cscs',
                          '/scratch/shared/fulen',
                          '/users'])
    username = getpass.getuser()
    time_limit = '5m'
    ior_binaries = fixture(build_ior_benchmarks, scope='environment')
    maintainers = ['SO', 'TM']
    tags = {'ops', 'production'}

    @run_after('init')
    def set_description(self):
        self.descr = f'IOR check ({self.base_dir})'

    @run_after('init')
    def add_fs_tags(self):
        self.tags |= {self.base_dir}

    @run_after('init')
    def set_fs_information(self):
        self.fs = {
            '/capstor/scratch/cscs': {
                'valid_systems': ['eiger:mc', 'pilatus:mc'],
                'eiger': {
                    'num_tasks': 10,
                },
                'pilatus': {
                    'num_tasks': 10,
                }
            },
            '/users': {
                'valid_systems': ['fulen:normal'],
                'ior_block_size': '8g',
                'daint': {},
                'dom': {},
                'fulen': {
                    'valid_prog_environs': ['PrgEnv-gnu']
                }
            },
            '/scratch/shared/fulen': {
                'valid_systems': ['fulen:normal'],
                'ior_block_size': '48g',
                'fulen': {
                    'num_tasks': 8,
                    'valid_prog_environs': ['PrgEnv-gnu']
                }
            }
        }

        # Setting some default values
        for data in self.fs.values():
            data.setdefault('ior_block_size', '24g')
            data.setdefault('ior_access_type', 'MPIIO')
            data.setdefault(
                'reference',
                {
                    'read_bw': (0, None, None, 'MiB/s'),
                    'write_bw': (0, None, None, 'MiB/s')
                }
            )
            data.setdefault('dummy', {})  # entry for unknown systems

    @run_after('init')
    def set_performance_reference(self):
        # Converting the references from each fs to per system.
        self.reference = {
            '*': self.fs[self.base_dir]['reference']
        }

    @run_after('init')
    def set_valid_systems(self):
        self.valid_systems = self.fs[self.base_dir]['valid_systems']

        cur_sys = self.current_system.name
        if cur_sys not in self.fs[self.base_dir]:
            cur_sys = 'dummy'

        vpe = 'valid_prog_environs'
        penv = self.fs[self.base_dir][cur_sys].get(vpe, ['builtin'])
        self.valid_prog_environs = penv

        tpn = self.fs[self.base_dir][cur_sys].get('num_tasks_per_node', 1)
        self.num_tasks = self.fs[self.base_dir][cur_sys].get('num_tasks', 1)
        self.num_tasks_per_node = tpn

    @run_after('init')
    def load_cray_module(self):
        if self.current_system.name in ['eiger', 'pilatus']:
            self.modules = ['cray']

    @run_before('run')
    def prepare_run(self):
        # Default umask is 0022, which generates file permissions -rw-r--r--
        # we want -rw-rw-r-- so we set umask to 0002
        os.umask(2)
        test_dir = os.path.join(self.base_dir, self.username, '.ior')
        test_file = os.path.join(test_dir,
                                 f'.ior.{self.current_partition.name}')
        self.prerun_cmds = [f'mkdir -p {test_dir}']
        self.executable = os.path.join(
            self.ior_binaries.stagedir,
            self.ior_binaries.build_prefix,
            'src', 'ior'
        )

        # executable options depends on the file system
        block_size = self.fs[self.base_dir]['ior_block_size']
        access_type = self.fs[self.base_dir]['ior_access_type']
        self.executable_opts += ['-F', '-C ', '-Q 1', '-t 4m', '-D 30',
                                 '-b', block_size, '-a', access_type,
                                 '-o', test_file, '--posix.odirect']

    @sanity_function
    def assert_finished(self):
        return sn.assert_found(r'^Finished\s+:', self.stdout)


@rfm.simple_test
class IorWriteCheck(IorCheck):
    executable_opts = ['-w', '-k']
    tags |= {'write'}

    @run_after('init')
    def set_perf_patterns(self):
        self.perf_patterns = {
            'write_bw': sn.extractsingle(
                r'^Operation(.*\n)*^write\s+(?P<write_bw>\S+)', self.stdout,
                'write_bw', float)
        }


@rfm.simple_test
class IorReadCheck(IorCheck):
    executable_opts = ['-r']
    tags |= {'read'}

    @run_after('init')
    def set_perf_patterns(self):
        self.perf_patterns = {
            'read_bw': sn.extractsingle(
                r'^Operation(.*\n)*^read\s+(?P<read_bw>\S+)', self.stdout,
                'read_bw', float)
        }

    @run_after('init')
    def set_deps(self):
        variant = IorWriteCheck.get_variant_nums(base_dir=self.base_dir)[0]
        self.depends_on(IorWriteCheck.variant_name(variant))
