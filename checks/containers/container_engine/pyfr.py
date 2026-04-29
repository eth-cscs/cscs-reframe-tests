# Copyright 2026 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import sys
import pathlib
import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.parent / 'config' / 'utilities'))

from uenv import uarch
from container_engine import ContainerEngineMixin  # noqa: E402
from slurm_mpi_pmix import SlurmMpiPmixMixin


@rfm.simple_test
class PyFR_CE(rfm.RunOnlyRegressionTest, ContainerEngineMixin, SlurmMpiPmixMixin):
    descr = 'PyFR for CE'
    valid_systems = ['+ce +nvgpu']
    valid_prog_environs = ['builtin']
    backend = parameter(['cuda'])
    test_name = parameter(['3d-taylor-green-ci'])
    maintainers = ['VCUE']
    tags = {'ce_dev'}

    num_tasks = 2
    num_tasks_per_node = 1
    time_limit = '3m'

    container_image = 'jfrog.svc.cscs.ch/ghcr/sarus-suite/containerfiles-ci/pyfr:2.1-ompi5.0.9-ofi1.22-cuda12.8.1'
    container_workdir = '/pyfr-test-cases/3d-taylor-green'
    container_env_table = {
        'env': {
            'UCX_WARN_UNUSED_ENV_VARS': 'n'
        }
    }
    regex_sim_complete = r'100\.0.* 5.00/5.00 ela: 00:00:(?P<sec>\d+) rem: 00:00:00$'

    reference_per_test = {
        '3d-taylor-green-ci': {
            'gh200': {
                'elapsed': (18.0, -0.10, 0.10, 's')
            },
            'a100': {
                'elapsed': (36.0, -0.10, 0.10, 's')
            }
        }
    }

    @run_after('setup')
    def set_executable(self):
        self.executable = f'pyfr'
        self.executable_opts = [
            f'-p',
            f'run',
            f'--backend {self.backend}',
            f'taylor-green-p2.pyfrm',
            f'taylor-green-ci.ini',
        ]

    @sanity_function
    def assert_sanity(self):
        s1 = sn.assert_found(self.regex_sim_complete, self.stderr)
        return sn.all([s1])

    @performance_function('s')
    def elapsed(self):
        return sn.extractsingle(self.regex_sim_complete, self.stderr, 'sec', float)

    @run_before('performance')
    def set_perf_reference(self):
        self.uarch = uarch(self.current_partition)
        if self.uarch is not None and \
           self.uarch in self.reference_per_test[self.test_name]:
            self.reference = {
                self.current_partition.fullname:
                    self.reference_per_test[self.test_name][self.uarch]
            }


@rfm.simple_test
class PyFR_Skybox(PyFR_CE):
    descr = 'PyFR for CE/Skybox'
    tags = {'ce_dev', 'skybox'}
    spank_option = 'edf'
    container_env_key_values = {
        'devices': ["alps.cscs/cxi=all", "nvidia.com/gpu=all", "/dev/gdrdrv"]
    }
