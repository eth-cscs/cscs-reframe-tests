# Copyright 2016 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from container_engine import ContainerEngineCPEMixin  # noqa: E402


class CudaNvmlBase(rfm.RegressionTest):
    descr = 'Checks that nvml can report GPU informations'
    build_locally = False
    build_system = 'SingleSource'
    sourcesdir = None
    maintainers = ['PA', 'SSA']

    @sanity_function
    def set_sanity(self):
        """
        Listing devices:
        0. NVIDIA A100-SXM4-80GB [00000000:03:00.0]
        Changing device's compute mode from 'Exclusive Process' to 'Prohibited'
        Need root privileges to do that: Insufficient Permissions # <-- OK

        Listing devices:
        0. NVIDIA A100-SXM4-80GB [00000000:03:00.0]
        Changing device's compute mode from 'Exclusive Process' to 'Prohibited'
        Need root privileges to do that: Insufficient Permissions # <-- OK
        """
        cp = self.current_partition
        self.gpu_count = cp.select_devices('gpu')[0].num_devices
        regex_devices = rf'Found {self.gpu_count} devices'
        regex_pciinfo = r'\d+.\s+(\S+\s+){2,}\[\S+\]'
        regex_mode = 'Need root privileges to do that: Insufficient Permission'
        return sn.all([
            sn.assert_found(regex_devices, self.stdout),
            sn.assert_found(regex_pciinfo, self.stdout),
            sn.assert_found(regex_mode, self.stdout),
        ])


@rfm.simple_test
class UENV_NVML(CudaNvmlBase):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+uenv +prgenv +cuda -cpe']
    tags = {'external-resources', 'health', 'uenv'}

    @run_after('setup')
    def setup_src(self):
        cuda_home = os.environ.get("CUDA_HOME")
        cuda_root = cuda_home if cuda_home is not None else (
            f"`echo $UENV_VIEW |cut -d: -f1`"
            f"/env"
            f"/`echo $UENV_VIEW |cut -d: -f3`"
        )
        self.sourcepath = f'{cuda_root}/nvml/example/example.c'
        self.prebuild_cmds = [f'echo "# sourcepath={self.sourcepath}"']
        self.build_system.cflags = [f'-I {cuda_root}/include']
        self.build_system.ldflags = [f'-L {cuda_root}/lib64 -lnvidia-ml']


@rfm.simple_test
class CPE_NVML(CudaNvmlBase, ContainerEngineCPEMixin):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+cuda +cpe -uenv -containerized_cpe']
    tags = {'external-resources', 'health', 'craype'}

    @run_after('init')
    def skip_uenv_tests(self):
        # it seems that valid_prog_environs ignores -uenv
        self.skip_if(os.environ.get("UENV") is not None)

    @run_after('setup')
    def setup_modules(self):
        sm = self.current_partition.select_devices('gpu')[0].arch[-2:]

        # FIXME Temporary workaround for cudatoolkit absence in ce image
        if 'containerized_cpe' not in self.current_environ.features:
            self.modules = ['cudatoolkit', f'craype-accel-nvidia{sm}']

        self.sourcepath = (
            '${CUDATOOLKIT_HOME:-$CUDA_HOME}/nvml/example/example.c'
        )

    @run_before('compile')
    def set_build_flags(self):
        self.prebuild_cmds = [
            'echo CUDATOOLKIT_HOME=${CUDATOOLKIT_HOME:-$CUDA_HOME}'
        ]
        self.build_system.cflags = [
            '-I ${CUDATOOLKIT_HOME:-$CUDA_HOME}/include']
        self.build_system.ldflags = [
            '-L ${CUDATOOLKIT_HOME:-$CUDA_HOME} -lnvidia-ml'
        ]

# ref         # Address the __gxx_personality_v0 symbol issue in lbmpi_gtl_cuda
# ref         if 'PrgEnv-gnu' == self.current_environ.name:
# ref             self.build_system.ldflags += ['-lstdc++']
