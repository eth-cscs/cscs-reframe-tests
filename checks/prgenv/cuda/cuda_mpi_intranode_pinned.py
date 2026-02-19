# Copyright ETHZ/CSCS
# See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

from reframe.core.builtins import xfail

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from uenv_slurm_mpi_options import UenvSlurmMpiOptionsMixin


@rfm.simple_test
class MPIIntranodePinned(rfm.RegressionTest, UenvSlurmMpiOptionsMixin):
    descr = 'Reproducer for slow intranode performance with pinned memory'
    valid_systems = ['+remote +nvgpu']
    valid_prog_environs = ['+uenv +prgenv -ce']
    sourcesdir = 'https://github.com/eth-cscs/alps-gh200-reproducers.git'
    prebuild_cmds = ['cd intranode-pinned-host-comm']
    prerun_cmds = ['cd intranode-pinned-host-comm']
    build_system = 'CMake'
    build_locally = False
    time_limit = '2m'
    tags = {'maintenance', 'uenv'}
    maintainers = ['SSA', 'VCUE', 'msimberg', 'perettig']
    executable = 'intranode_pinned_host_comm'
    mem = parameter(['host', 'pinned_host'])
    # This has no effect with OpenMPI
    mpich_smp_single_copy_mode = parameter(['CMA', 'XPMEM'])

    @run_after('setup')
    def setup_job(self):
        self.num_tasks = 2
        self.num_tasks_per_node = 2
        self.job.launcher.options += ['--cpu-bind=sockets']
        self.env_vars['MPICH_SMP_SINGLE_COPY_MODE'] = self.mpich_smp_single_copy_mode
	# Always disabled GPU support to avoid Cray MPICH's fallback to CMA
	# when GPU support is enabled (XPMEM is the default if GPU support is
	# disabled). Some clusters set MPICH_GPU_SUPPORT_ENABLED=1 and some
	# leave it unset.
        self.env_vars['MPICH_GPU_SUPPORT_ENABLED'] = '0'

    @run_before('run')
    def set_exe_opts(self):
        self.executable_opts = ['2', '5', self.mem, str(1 << 27)]

    @sanity_function
    def validate(self):
        return sn.assert_found(r'rank 0 to rank 1', self.stdout)

    @performance_function('s')
    def time_value(self):
        regex = r'\[1:4]\s*time:\s*(?P<sec>\S+)'
        return sn.extractsingle(regex, self.stdout, 'sec', float)

    @run_after('setup')
    def set_reference(self):
        if "openmpi" in self.current_environ.features:
            ref = (0.056, None, 0.15, "s")
        elif self.mem == "pinned_host" or self.mpich_smp_single_copy_mode == "XPMEM":
            ref = xfail("Known issue with pinned memory", (0.003, None, 0.15, "s"))
        else:
            ref = (0.003, None, 0.15, "s")
        self.reference = {"*": {"time_value": ref}}
