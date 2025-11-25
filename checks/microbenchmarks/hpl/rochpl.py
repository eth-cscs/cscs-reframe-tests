# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from uenv import uarch

rochpl_references = {
    'mi200': {38400: 2.65e+04, 192000: 1.49e+05, 218880: 1.55e+05},
    'mi300': {38400: 2.53e+04, 192000: 1.57e+05, 218880: 1.62e+05},
}

slurm_config = {
    'mi200': {
        'ntasks-per-node': 8,
        'cpus-per-task': 16,
    },
    'mi300': {
        'ntasks-per-node': 4,
        'cpus-per-task': 48,
    }
}

HPLdat = """HPLinpack benchmark input file
Innovative Computing Laboratory, University of Tennessee
HPL.out      output file name (if any)
0            device out (6=stdout,7=stderr,file)
{count}      # of problems sizes (N)
{sizes}      Ns
1            # of NBs
384          NBs
1            PMAP process mapping (0=Row-,1=Column-major)
1            # of process grids (P x Q)
{p}          Ps
{q}          Qs
16.0         threshold
1            # of panel fact
2            PFACTs (0=left, 1=Crout, 2=Right)
1            # of recursive stopping criterium
8            NBMINs (>= 1)
1            # of panels in recursion
2            NDIVs
1            # of recursive panel fact.
2            RFACTs (0=left, 1=Crout, 2=Right)
1            # of broadcast
6            BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)
1            # of lookahead depth
1            DEPTHs (>=0)
1            SWAP (0=bin-exch,1=long,2=mix)
64           swapping threshold
1            L1 in (0=transposed,1=no-transposed) form
0            U  in (0=transposed,1=no-transposed) form
0            Equilibration (0=no,1=yes)
8            memory alignment in double (> 0)
"""


class RocHPL(rfm.RegressionTest):
    descr = 'AMD HPL (rocHPL) test'
    valid_systems = ['+amdgpu +uenv']
    valid_prog_environs = ['+uenv +prgenv +rocm']
    maintainers = ['rasolca', 'SSA']
    sourcesdir = 'scripts'
    build_system = 'CMake'
    # This branch contains fixes for cmake.
    # https://github.com/ROCm/rocHPL/pull/28
    prebuild_cmds = [
        'git clone --depth 1 --branch cmake_hip '
        'https://github.com/rasolca/rocHPL.git'
    ]
    time_limit = '10m'
    build_locally = False

    @run_before('compile')
    def set_build_options(self):
        self.build_system.configuredir = 'rocHPL'
        self.build_system.builddir = 'build'
        self.build_system.max_concurrency = 10

        gpu_arch = self.current_partition.select_devices('gpu')[0].arch
        self.build_system.config_opts = [
            '-DHPL_VERBOSE_PRINT=ON',
            '-DHPL_PROGRESS_REPORT=ON',
            '-DHPL_DETAILED_TIMING=ON',
            '-DCMAKE_BUILD_TYPE=Release',
            f'-DCMAKE_HIP_ARCHITECTURES="{gpu_arch}"'
        ]

    @run_after('setup')
    def set_num_gpus(self):
        curr_part = self.current_partition
        self.num_gpus = curr_part.select_devices('gpu')[0].num_devices

    @run_before('run')
    def set_executable(self):
        self.uarch = uarch(self.current_partition)

        pre_script = f'./{self.uarch}-wrapper.sh'
        binary = os.path.join(self.build_system.builddir, 'bin', 'rochpl')
        self.executable = f'{pre_script} {binary}'

        # slurm configuration
        config = slurm_config[self.uarch]
        self.job.options = [f'--nodes=1']
        self.num_tasks_per_node = config['ntasks-per-node']
        self.num_tasks = self.num_tasks_per_node
        self.num_cpus_per_task = config['cpus-per-task']
        self.ntasks_per_core = 2
        if self.uarch == 'mi200':
            self.job.launcher.options = [(
                '--cpu-bind=mask_cpu:'
                'ff00000000000000ff000000000000,'
                'ff00000000000000ff00000000000000,'
                'ff00000000000000ff0000,'
                'ff00000000000000ff000000,'
                'ff00000000000000ff,'
                'ff00000000000000ff00,'
                'ff00000000000000ff00000000,'
                'ff00000000000000ff0000000000')]
        else:
            self.job.launcher.options = ['--cpu-bind=cores']

        # env variables
        self.env_vars['MPICH_GPU_SUPPORT_ENABLED'] = '1'
        self.env_vars['OMP_PROC_BIND'] = 'true'
        self.env_vars['OMP_NUM_THREADS'] = \
            f'{self.num_cpus_per_task / self.ntasks_per_core}'

        # executable options
        if self.uarch == 'mi200':
            prows = 2
            pcols = 4
        if self.uarch == 'mi300':
            prows = 2
            pcols = 2

        input_file = os.path.join(self.stagedir, 'HPL.dat')
        with open(input_file, 'w') as file:
            file.write(HPLdat.format(count=len(self.matrix_sizes), sizes=' '.join(str(n) for n in self.matrix_sizes), p=prows, q=pcols))  # noqa: E501

        self.executable_opts += [
            f'-p {prows}',
            f'-q {pcols}',
            f'-P {prows}',
            f'-Q {pcols}',
            f'-i {input_file}'
        ]

        # set performance reference
        if self.uarch in rochpl_references:
            reference = {}

            for n in self.matrix_sizes:
                if n in rochpl_references[self.uarch]:
                    # Note: Permissive threshold for mi300 as sles15sp5 shows
                    # performance drops with large matrices. Should be removed
                    # when all the nodes run the sles15sp6 image.
                    lower_bound = -0.1
                    if self.uarch == 'mi300':
                        if n > 200000:
                            lower_bound = -0.90
                        elif n > 150000:
                            lower_bound = -0.33

                    reference[f'size {n}'] = \
                        (rochpl_references[self.uarch][n],
                         lower_bound, 0.05, 'Gflop/s')

            self.reference = {self.current_partition.fullname: reference}

    @sanity_function
    def assert_results(self):
        """
        WC15R2R8      218880   384     2     2             102.52              6.819e+04
        ||Ax-b||_oo/(eps*(||A||_oo*||x||_oo+||b||_oo)*N)=        0.0000524 ...... PASSED
        """
        out_file = os.path.join(self.stagedir, 'HPL.out')

        regex1 = r'^WC15R2R8\s+([0-9]+)\s+384\s+[0-9]+\s+[0-9]+\s+[0-9\.]+\s+([0-9\.]+e\+[0-9]+)$'
        regex2 = r'^\|\|Ax-b\|\|_oo\/\(eps\*\(\|\|A\|\|_oo\*\|\|x\|\|_oo\+\|\|b\|\|_oo\)\*N\)=\s+([\.0-9]+)\s+\.+\s+PASSED$'
        self.perf_ = sn.extractall(regex1, out_file, tag=(1, 2), conv=(int, float))
        self.accuracy_ = sn.extractall(regex2, out_file, tag=1, conv=float)

        sanity_patterns = [
            sn.assert_eq(sn.len(self.perf_), sn.len(self.matrix_sizes), 'Number of results do not match with number of runs'),
            sn.assert_eq(sn.len(self.accuracy_), sn.len(self.matrix_sizes), 'Number of PASSED accuracy results do not match with number of runs')
            ]

        for (perf, n) in sn.zip(self.perf_, self.matrix_sizes):
            sanity_patterns.append(sn.assert_eq(perf[0], n, 'Matrix size does not match'))

        self.sanity_patterns = sn.all(sanity_patterns)

        return self.sanity_patterns

    @run_before('performance')
    def set_perf_vars(self):
        make_perf = sn.make_performance_function

        self.perf_variables = {}
        for perf in self.perf_:
            self.perf_variables[f'size {perf[0]}'] = make_perf(sn.getitem(perf, 1), 'Gflop/s')


@rfm.simple_test
class RocHPL_small(RocHPL):
    matrix_sizes = [38400]


@rfm.simple_test
class RocHPL_medium(RocHPL):
    matrix_sizes = [192000]
    tags = {'production', 'uenv', 'bencher'}


@rfm.simple_test
class RocHPL_large(RocHPL):
    matrix_sizes = [218880]
    tags = {'production', 'uenv', 'bencher'}
