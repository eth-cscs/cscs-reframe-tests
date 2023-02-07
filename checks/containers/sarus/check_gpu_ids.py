import os
import sys

import reframe as rfm
import reframe.utility.sanity as sn


sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class BaseCheck(rfm.RunOnlyRegressionTest):
    valid_systems = []
    valid_prog_environs = ['builtin']
    sourcesdir = None
    modules = ['sarus']
    num_tasks = 1
    num_tasks_per_node = 1
    num_gpus_per_node = 1
    sarus_image = 'ethcscs/cudasamples:8.0'
    maintainers = ['amadonna', 'taliaga']
    tags = {'production'}

    @run_after('setup')
    def setup_prerun(self):
        self.prerun_cmds = ['sarus --version',
                            f'sarus pull {self.sarus_image}']

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r'CHECK SUCCESSFUL', self.stdout)


@rfm.simple_test
class SarusNvidiaSmiCheck(BaseCheck):
    @run_after('setup')
    def setup_exec(self):
        abs_dirname = os.path.abspath(os.path.dirname(__file__))
        self.executable = 'python'
        self.executable_opts = [
            f'{abs_dirname}/compare_output_of_native_and_shifter_nvidia_smi.py'
        ]


@rfm.simple_test
class SarusDeviceQueryCheck(BaseCheck):
    @run_after('setup')
    def setup_exec(self):
        abs_dirname = os.path.abspath(os.path.dirname(__file__))
        self.executable = 'python'
        self.executable_opts = [
            f'{abs_dirname}/compare_order_of_nvidia_devices.py'
        ]
