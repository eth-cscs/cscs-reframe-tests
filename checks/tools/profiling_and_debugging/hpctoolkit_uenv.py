# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class HPCToolkit(rfm.RegressionTest):
    descr = 'https://hpctoolkit.org test'
    valid_systems = ['+nvgpu +uenv']
    valid_prog_environs = ['+uenv +hpctoolkit +py-hatchet']
    maintainers = ['SSA', 'jgphpc']
    tags = {'production', 'uenv', 'benchmark'}

    repo = 'https://github.com/sekelle/cornerstone-octree'
    sourcesdir = 'src/hpctoolkit'
    build_system = 'CMake'
    time_limit = '3m'
    build_locally = False
    sph_build_type = parameter(['Debug'])

    exe = 'hilbert_perf_gpu'
    num_gpus = 4
    ntasks_per_node = variable(int, value=4)

    @run_before('compile')
    def build_step(self):
        self.build_system.configuredir = f'{self.repo.split("/")[-1]}-master'
        self.prebuild_cmds = [
            f'wget -q {self.repo}/archive/refs/heads/master.zip',
            f'unzip -q master.zip',
            f'patch -p 1 -d {self.build_system.configuredir}'
            f' -i ../hilbert.patch'
        ]
        self.build_system.builddir = 'build'
        self.build_system.config_opts = [
            f'-DCSTONE_WITH_HIP=OFF', f'-DCSTONE_WITH_CUDA=ON',
            f'-DCSTONE_WITH_GPU_AWARE_MPI=ON',
            f'-DCMAKE_BUILD_TYPE={self.sph_build_type}',
        ]
        self.build_system.max_concurrency = 64
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch
        gpu_arch = (
            gpu_arch[len("sm_"):]
            if gpu_arch.startswith("sm_")
            else gpu_arch
        )
        self.build_system.config_opts += [
            f'-DCMAKE_CUDA_ARCHITECTURES="{gpu_arch}"'
        ]
        self.build_system.make_opts = [self.exe]

    @run_before('run')
    def set_executable(self):
        self.executable = ''.join((
            f'hpcrun -e gpu=cuda -e PAPI_TOT_CYC -t ',
            os.path.join(self.build_system.builddir,
                         'test', 'performance', self.exe))
        )
        self.num_tasks = self.num_gpus
        self.num_tasks_per_node = self.ntasks_per_node
        self.prerun_cmds = [
            f'echo "# SLURM_JOBID=$SLURM_JOBID"',
        ]
        self.postrun_cmds = [
            'time -p hpcstruct hpctoolkit-hilbert_perf_gpu-measurements-*',
            'time -p hpcprof hpctoolkit-hilbert_perf_gpu-measurements-*',
            'time -p ./stats.py hpctoolkit-hilbert_perf_gpu-database-*',
            'dot -T svg _rpt.dot > _rpt.svg',
            'file _rpt.svg'
        ]

    @sanity_function
    def assert_results(self):
        regex_h2d = r' (?P<GXCOPY_H2D>\S+)\.000 main src'
        sum1 = sn.sum(sn.extractall(regex_h2d, self.stdout, 'GXCOPY_H2D', int))

        regex_h2d_df = r'# direct sum over ranks: (?P<GXCOPY_H2D>\S+)\.000'
        sum2 = sn.extractsingle(regex_h2d_df, self.stdout, 'GXCOPY_H2D', int)

        return sn.assert_eq(sum1, sum2)
