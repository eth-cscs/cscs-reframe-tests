# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
import os
# import shutil

import reframe as rfm
# from hpctestlib.sciapps.gromacs.benchmarks import gromacs_check
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
from uenv import uarch
# import uenv

gromacs_references = {
    'STMV'          : {'gh200': {'time_run': (117, None, None, 'ns/day')}},
    'hEGFRDimerPair': {'gh200': {'time_run': (56, None, None, 'ns/day')}},
}

slurm_config = {
    'STMV': {
        'gh200': {
            'nodes': 1,
            'ntasks-per-node': 8,
            'cpus-per-task': 32,
            'walltime': '0d0h5m0s',
            'gpu': True,
        }
    },
    'hEGFRDimerPair': {
        'gh200': {
            'nodes': 1,
            'ntasks-per-node': 8,
            'cpus-per-task': 32,
            'walltime': '0d0h5m0s',
            'gpu': True,
        }
    },
}


class gromacs_download(rfm.RunOnlyRegressionTest):
    descr = 'Fetch GROMACS source code'
    maintainers = ['SSA']
    version = variable(str, value='2024.3')
    sourcesdir = None
    executable = 'wget'
    executable_opts = [
        '--quiet',
        'https://jfrog.svc.cscs.ch/artifactory/cscs-reframe-tests/gromacs/'
        f'v{version}.tar.gz',
        # https://github.com/gromacs/gromacs/archive/refs/tags/v2024.3.tar.gz
    ]
    local = True

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class gromacs_build_test(rfm.CompileOnlyRegressionTest):
    """
    Test GROMACS build from source using the develop view
    """
    descr = 'GROMACS Build Test'
    valid_prog_environs = ['+gromacs-dev']
    valid_systems = ['*']
    build_system = 'CMake'
    maintainers = ['SSA']
    sourcesdir = None
    gromacs_sources = fixture(gromacs_download, scope='session')
    build_locally = False
    tags = {'uenv'}

    @run_before('compile')
    def prepare_build(self):
        self.uarch = uarch(self.current_partition)
        # self.build_system.builddir = os.path.join(self.stagedir, 'build')
        self.skip_if_no_procinfo()
        cpu = self.current_partition.processor
        self.build_system.max_concurrency = cpu.info['num_cpus_per_socket']
        tarsource = os.path.join(
            self.gromacs_sources.stagedir,
            f'v{self.gromacs_sources.version}.tar.gz'
        )
        self.prebuild_cmds = [f'tar --strip-components=1 -xzf {tarsource}']
        self.build_system.config_opts = [
            '-DREGRESSIONTEST_DOWNLOAD=ON',
            '-DGMX_MPI=on',
            '-DGMX_BUILD_OWN_FFTW=ON',
            '-DCP2K_USE_SPGLIB=ON',
            '-DGMX_HWLOC=ON',
            '-DGMX_SIMD=ARM_NEON_ASIMD',
            '-DGMX_INSTALL_NBLIB_API=ON',
        ]
        if self.uarch == 'gh200':
            self.build_system.config_opts += ['-DGMX_GPU=CUDA']

    @sanity_function
    def validate_test(self):
        folder = 'bin' # add folder path
        self.gromacs_executable = os.path.join('bin', 'gmx_mpi')
        print(self.gromacs_executable)
        return os.path.isfile(self.gromacs_executable)

@rfm.simple_test
class gromacs_run_test(rfm.RunOnlyRegressionTest):
    executable = './mps-wrapper.sh -- gmx_mpi mdrun -s topol.tpr'
    executable_opts = ['-dlb no', '-ntomp 32', '-pme gpu', '-npme 1', '-bonded gpu', '-nb gpu', '-nsteps 10000', '-update gpu', '-pin off', '-v', '-noconfout', '-nstlist 300']
    maintainers = ['SSA']
    valid_systems = ['*']
    test_name = variable(str, value='STMV')
    valid_prog_environs = ['+gromacs']

    @run_before('run')
    def prepare_run(self):
        self.uarch = uarch(self.current_partition)
        config = slurm_config[self.test_name][self.uarch]
        # sbatch options
        self.job.options = [
            f'--nodes={config["nodes"]}',
        ]
        self.num_tasks_per_node = config['ntasks-per-node']
        self.num_tasks = config['nodes'] * self.num_tasks_per_node
        self.num_cpus_per_task = config['cpus-per-task']
        self.time_limit = config['walltime']

        # environment variables
        self.env_vars['OMP_NUM_THREADS'] = str(self.num_cpus_per_task)
        self.env_vars['FI_CXI_RX_MATCH_MODE'] = 'software'

        if self.uarch == 'gh200':

            self.env_vars['MPICH_GPU_SUPPORT_ENABLED'] = '1'
            self.env_vars['GMX_GPU_DD_COMMS'] = 'true'
            self.env_vars['GMX_GPU_PME_PP_COMMS'] = 'true'
            self.env_vars['GMX_ENABLE_DIRECT_GPU_COMM'] = '1'
            self.env_vars['GMX_FORCE_GPU_AWARE_MPI'] = '1'

        # set reference
        if self.uarch is not None and \
           self.uarch in gromacs_references[self.test_name]:
            self.reference = {
                self.current_partition.fullname:
                    gromacs_references[self.test_name][self.uarch]
            }
        
        # set input files
        if self.test_name == 'STMV':
            self.prerun_cmds = ['wget https://jfrog.svc.cscs.ch/artifactory/cscs-reframe-tests/gromacs/STMV/topol.tpr']


    @run_after('setup')
    def postproc_run(self):
        # extract Bond Energy from the binary .edr file and write it to a readable .xvg file and then write it to stdout
        self.postrun_cmds = [
            'echo -e "1\n" |'
            'gmx_mpi energy -f ener.edr -o ener.xvg',
            'cat ener.xvg'
        ]
        
    @sanity_function
    def validate_bond_energy(self):
        # RegEx to extract from ener.xvg
        regex = r'^@.*\"Bond\"\n\s+\S+\s+(?P<energy>\S+)$'
        energy = sn.avg(sn.extractall(regex, self.stdout, 'energy', float))

        energy_reference = 164780.14
        energy_diff = sn.abs(energy - energy_reference)

        sn.assert_lt(energy_diff, 1644) #1% tolerance

    @performance_function('ns/day')
    def time_run(self):
        # RegEx to extract from slurm-XXX.out
        return sn.extractsingle(
                r'^Performance:\s+(?P<nspd>\S+)\s+',
                self.stderr,
                'ns_day',
                float,
            )

# @rfm.simple_test
# class cscs_gromacs_check(gromacs_check):
#     modules = ['GROMACS']
#     maintainers = ['@victorusu']
#     use_multithreading = False
#     extra_resources = {
#         'switches': {
#             'num_switches': 1
#         }
#     }
#     executable_opts += ['-dlb yes', '-ntomp 1', '-npme -1']
#     valid_prog_environs = ['builtin']

#     # CSCS-specific parameterization
#     num_nodes = parameter([1, 2, 4, 6, 8, 16], loggable=True)
#     allref = {
#         1: {g
#             'sm_60': {
#                 'HECBioSim/Crambin': (195.0, None, None, 'ns/day'),
#                 'HECBioSim/Glutamine-Binding-Protein': (78.0, None, None, 'ns/day'),   # noqa: E501
#                 'HECBioSim/hEGFRDimer': (8.5, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (9.2, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (3.0, None, None, 'ns/day'),
#             },
#             'broadwell': {
#                 'HECBioSim/Crambin': (116.0, None, None, 'ns/day'),
#                 'HECBioSim/Glutamine-Binding-Protein': (38.0, None, None, 'ns/day'),   # noqa: E501
#                 'HECBioSim/hEGFRDimer': (4.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (8.0, None, None, 'ns/day'),
#             },
#             'zen2': {
#                 'HECBioSim/Crambin': (320.0, None, None, 'ns/day'),
#                 'HECBioSim/Glutamine-Binding-Protein': (120.0, None, None, 'ns/day'),  # noqa: E501
#                 'HECBioSim/hEGFRDimer': (16.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (31.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (7.0, None, None, 'ns/day'),
#             },
#         },
#         2: {
#             'sm_60': {
#                 'HECBioSim/Crambin': (202.0, None, None, 'ns/day'),
#                 'HECBioSim/Glutamine-Binding-Protein': (111.0, None, None, 'ns/day'),  # noqa: E501
#                 'HECBioSim/hEGFRDimer': (15.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (18.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (6.0, None, None, 'ns/day'),
#             },
#             'broadwell': {
#                 'HECBioSim/Crambin': (200.0, None, None, 'ns/day'),
#                 'HECBioSim/Glutamine-Binding-Protein': (65.0, None, None, 'ns/day'),  # noqa: E501
#                 'HECBioSim/hEGFRDimer': (8.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (13.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (4.0, None, None, 'ns/day'),
#             },
#             'zen2': {
#                 'HECBioSim/Crambin': (355.0, None, None, 'ns/day'),
#                 'HECBioSim/Glutamine-Binding-Protein': (210.0, None, None, 'ns/day'),  # noqa: E501
#                 'HECBioSim/hEGFRDimer': (31.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (53.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (13.0, None, None, 'ns/day'),
#             },
#         },
#         4: {
#             'sm_60': {
#                 'HECBioSim/Crambin': (200.0, None, None, 'ns/day'),
#                 'HECBioSim/Glutamine-Binding-Protein': (133.0, None, None, 'ns/day'),  # noqa: E501
#                 'HECBioSim/hEGFRDimer': (22.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (28.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (10.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRtetramerPair': (5.0, None, None, 'ns/day'),
#             },
#             'broadwell': {
#                 'HECBioSim/Crambin': (260.0, None, None, 'ns/day'),
#                 'HECBioSim/Glutamine-Binding-Protein': (111.0, None, None, 'ns/day'),  # noqa: E501
#                 'HECBioSim/hEGFRDimer': (15.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (23.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (7.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRtetramerPair': (3.0, None, None, 'ns/day'),
#             },
#             'zen2': {
#                 'HECBioSim/Crambin': (340.0, None, None, 'ns/day'),
#                 'HECBioSim/Glutamine-Binding-Protein': (230.0, None, None, 'ns/day'),  # noqa: E501
#                 'HECBioSim/hEGFRDimer': (56.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (80.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (25.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRtetramerPair': (11.0, None, None, 'ns/day'),
#             },
#         },
#         6: {
#             'sm_60': {
#                 'HECBioSim/Crambin': (213.0, None, None, 'ns/day'),
#                 'HECBioSim/Glutamine-Binding-Protein': (142.0, None, None, 'ns/day'),  # noqa: E501
#                 'HECBioSim/hEGFRDimer': (28.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (29.346, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (13.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRtetramerPair': (8.0, None, None, 'ns/day'),
#             },
#             'broadwell': {
#                 'HECBioSim/Crambin': (308.0, None, None, 'ns/day'),
#                 'HECBioSim/Glutamine-Binding-Protein': (127.0, None, None, 'ns/day'),  # noqa: E501
#                 'HECBioSim/hEGFRDimer': (22.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (29.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (9.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRtetramerPair': (5.0, None, None, 'ns/day'),
#             },
#             'zen2': {
#                 'HECBioSim/Glutamine-Binding-Protein': (240.0, None, None, 'ns/day'),  # noqa: E501
#                 'HECBioSim/hEGFRDimer': (75.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (110.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (33.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRtetramerPair': (13.0, None, None, 'ns/day'),
#             },
#         },
#         8: {
#             'sm_60': {
#                 'HECBioSim/Crambin': (206.0, None, None, 'ns/day'),
#                 'HECBioSim/Glutamine-Binding-Protein': (149.0, None, None, 'ns/day'),  # noqa: E501
#                 'HECBioSim/hEGFRDimer': (37.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (39.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (16.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRtetramerPair': (9.0, None, None, 'ns/day'),
#             },
#             'broadwell': {
#                 'HECBioSim/Crambin': (356.0, None, None, 'ns/day'),
#                 'HECBioSim/Glutamine-Binding-Protein': (158.0, None, None, 'ns/day'),  # noqa: E501
#                 'HECBioSim/hEGFRDimer': (28.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (39.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (11.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRtetramerPair': (6.0, None, None, 'ns/day'),
#             },
#             'zen2': {
#                 'HECBioSim/Glutamine-Binding-Protein': (250.0, None, None, 'ns/day'),   # noqa: E501
#                 'HECBioSim/hEGFRDimer': (80.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (104.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (43.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRtetramerPair': (20.0, None, None, 'ns/day'),
#             },
#         },
#         16: {
#             'sm_60': {
#                 'HECBioSim/Glutamine-Binding-Protein': (154.0, None, None, 'ns/day'),  # noqa: E501
#                 'HECBioSim/hEGFRDimer': (43.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (41.889, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (21.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRtetramerPair': (14.0, None, None, 'ns/day'),
#             },
#             'broadwell': {
#                 'HECBioSim/Glutamine-Binding-Protein': (200.0, None, None, 'ns/day'),  # noqa: E501
#                 'HECBioSim/hEGFRDimer': (44.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (31.47, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (19.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRtetramerPair': (10.0, None, None, 'ns/day'),
#             },
#             'zen2': {
#                 'HECBioSim/hEGFRDimer': (82.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerSmallerPL': (70.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRDimerPair': (49.0, None, None, 'ns/day'),
#                 'HECBioSim/hEGFRtetramerPair': (25.0, None, None, 'ns/day'),
#             },
#         }
#     }

#     @run_after('init')
#     def setup_filtering_criteria(self):
#         # Update test's description
#         self.descr += f' ({self.num_nodes} node(s))'

#         # Setup system filtering
#         valid_systems = {
#             'cpu': {
#                 1: ['daint:mc', 'dom:mc', 'eiger:mc', 'pilatus:mc'],
#                 2: ['daint:mc', 'dom:mc', 'eiger:mc', 'pilatus:mc'],
#                 4: ['daint:mc', 'dom:mc', 'eiger:mc', 'pilatus:mc'],
#                 6: ['daint:mc', 'dom:mc', 'eiger:mc', 'pilatus:mc'],
#                 8: ['daint:mc', 'eiger:mc'],
#                 16: ['daint:mc', 'eiger:mc']
#             },
#             'gpu': {
#                 1: ['daint:gpu', 'dom:gpu', 'eiger:gpu', 'pilatus:gpu'],
#                 2: ['daint:gpu', 'dom:gpu', 'eiger:gpu', 'pilatus:gpu'],
#                 4: ['daint:gpu', 'dom:gpu', 'eiger:gpu', 'pilatus:gpu'],
#                 6: ['daint:gpu', 'dom:gpu', 'eiger:gpu', 'pilatus:gpu'],
#                 8: ['daint:gpu', 'eiger:gpu'],
#                 16: ['daint:gpu', 'eiger:gpu']
#             }
#         }
#         try:
#             self.valid_systems = valid_systems[self.nb_impl][self.num_nodes]
#         except KeyError:
#             self.valid_systems = []

#         # Setup prog env. filtering
#         if self.current_system.name in ('eiger', 'pilatus'):
#             self.valid_prog_environs = ['cpeGNU']

#         if self.num_nodes in (6, 16):
#             self.tags |= {'production'}
#             if (self.nb_impl == 'gpu' and
#                 self.bench_name == 'HECBioSim/hEGFRDimerSmallerPL'):
#                 self.tags |= {'maintenance'}

#     @run_before('run')
#     def setup_run(self):
#         self.skip_if_no_procinfo()

#         # Setup GPU run
#         if self.nb_impl == 'gpu':
#             self.num_gpus_per_node = 1
#             self.env_vars = {'CRAY_CUDA_MPS': 1}

#         proc = self.current_partition.processor

#         # Choose arch; we set explicitly the GPU arch, since there is no
#         # auto-detection
#         arch = proc.arch
#         if self.current_partition.fullname in ('daint:gpu', 'dom:gpu'):
#             arch = 'sm_60'

#         try:
#             found = self.allref[self.num_nodes][arch][self.bench_name]
#         except KeyError:
#             self.skip(f'Configuration with {self.num_nodes} node(s) of '
#                       f'{self.bench_name!r} is not supported on {arch!r}')

#         # Setup performance references
#         self.reference = {
#             '*': {
#                 'perf': self.allref[self.num_nodes][arch][self.bench_name]
#             }
#         }

#         # Setup parallel run
#         self.num_tasks_per_node = proc.num_cores
#         self.num_tasks = self.num_nodes * self.num_tasks_per_node
