import json
import pathlib
import re
import sys

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.osext as osext

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from extra_launcher_options import ExtraLauncherOptionsMixin
from sarus_extra_launcher_options import SarusExtraLauncherOptionsMixin
from cuda_visible_devices_all import CudaVisibleDevicesAllMixin

class sirius_scf_base_test(rfm.RunOnlyRegressionTest):
    test_folder = parameter(['Si63Ge'])
    executable = 'sirius.scf'
    strict_check = False
    use_multithreading = False
    maintainers = ['antonk']
    data_ref = 'output_ref.json'
    output_file = 'output.json'
    executable_opts = [f'--output={output_file}']

    @run_after('init')
    def setup_test(self):
        self.descr = 'Sirius SCF check'
        #self.env_vars = {
        #    'MPICH_OFI_STARTUP_CONNECT': 1,
        #    'OMP_PLACES': 'cores',
        #    'OMP_PROC_BIND': 'close'
        #}

        if self.current_system.name in {'hohgant'}:
            self.num_tasks_per_node = 4
            self.num_cpus_per_task = 16
            self.num_tasks_per_core = 1
            self.env_vars = {
                'OMP_NUM_THREADS': str(self.num_cpus_per_task)
            }

    @run_after('setup')
    def set_test_dir(self):
        self.sourcesdir = self.test_folder

    @run_before('sanity')
    def load_json_data(self):
        with osext.change_dir(self.stagedir):
            with open(self.output_file) as f:
                try:
                    self.output_data = json.load(f)
                except json.JSONDecodeError as e:
                    raise SanityError(
                        f'failed to parse JSON file {self.output_file}') from e

            with open(self.data_ref) as f:
                try:
                    self.reference_data = json.load(f)
                except json.JSONDecodeError as e:
                    raise SanityError(
                        f'failed to parse JSON file {self.data_ref}') from e

    @deferrable
    def energy_diff(self):
        ''' Return the difference between obtained and reference total energies'''
        return sn.abs(self.output_data['ground_state']['energy']['total'] -
                      self.reference_data['ground_state']['energy']['total'])

    @deferrable
    def stress_diff(self):
        ''' Return the difference between obtained and reference stress tensor components'''
        if ('stress' in self.output_data['ground_state'] and
            'stress' in self.reference_data['ground_state']):
            return sn.sum(
                sn.abs(self.output_data['ground_state']['stress'][i][j] -
                       self.reference_data['ground_state']['stress'][i][j])
                for i in [0, 1, 2] for j in [0, 1, 2]
            )
        else:
            return sn.abs(0)

    @deferrable
    def forces_diff(self):
        ''' Return the difference between obtained and reference atomic forces'''
        if ('forces' in self.output_data['ground_state'] and
            'forces' in self.reference_data['ground_state']):
            na = self.output_data['ground_state']['num_atoms']
            return sn.sum(
                sn.abs(self.output_data['ground_state']['forces'][i][j] -
                       self.reference_data['ground_state']['forces'][i][j])
                for i in range(na) for j in [0, 1, 2]
            )
        else:
            return sn.abs(0)

    @sanity_function
    def assert_success(self):
        return sn.all([
            sn.assert_found(r'converged after', self.stdout,
                            msg="Calculation didn't converge"),
            sn.assert_lt(self.energy_diff(), 1e-5,
                         msg="Total energy is different"),
            sn.assert_lt(self.stress_diff(), 1e-5,
                         msg="Stress tensor is different"),
            sn.assert_lt(self.forces_diff(), 1e-5,
                         msg="Atomic forces are different")
        ])


@rfm.simple_test
class SARUS_sirius_scf_check(sirius_scf_base_test,
                             SarusExtraLauncherOptionsMixin,
                             CudaVisibleDevicesAllMixin):
    container_image = variable(str, type(None), value=None)
    valid_systems = ['+sarus']
    valid_prog_environs = ['builtin']
    tags = {'parallel_k'}

    @run_after('setup')
    def setup_container_platform(self):
        # if container_image was provided then initialize a container execution
        if self.container_image is not None:
            self.container_platform = 'Sarus'
            self.container_platform.image = self.container_image
            self.container_platform.with_mpi = False
            self.container_platform.pull_image = False
            self.container_platform.command = (
                f'{self.executable} {" ".join(self.executable_opts)}'
            )
        else:
            raise ConfigError('container_image is not set')


@rfm.simple_test
class UENV_sirius_scf_check(sirius_scf_base_test,
                            ExtraLauncherOptionsMixin,
                            CudaVisibleDevicesAllMixin):
    valid_systems = ['+uenv -amdgpu']
    valid_prog_environs = ['+sirius +mpi +openmp']
    tags = {'parallel_k'}

