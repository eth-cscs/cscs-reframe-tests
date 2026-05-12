import json
import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.osext as osext

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from extra_launcher_options import ExtraLauncherOptionsMixin
from sarus_extra_launcher_options import SarusExtraLauncherOptionsMixin
from cuda_visible_devices_all import CudaVisibleDevicesAllMixin

sirius_tests = {
    # R:total number of MPI ranks, T:threads per rank, P:walltime
    'Si63Ge': {
        'zen2': {
            # zen2 cpu nodes: 2sockets, 8 numa, 16c/numa = 128c (no MT)
            'performance_reference': [{'R': 32, 'T': 4, 'P': 0}]
        },
        'zen3-4x-gpu-sm_80': {
            # A100 nodes: 1socket, 4 numa, 16c/numa = 64c (no MT)
            'performance_reference': [{'R': 4, 'T': 16, 'P': 0}]
        }
    }
}

class SIRIUSBase(rfm.RunOnlyRegressionTest):
    test_name = parameter(['Si63Ge'])
    descr = 'Sirius SCF check'
    executable = 'sirius.scf'
    strict_check = False
    use_multithreading = False
    maintainers = ['antonk']
    data_ref = 'output_ref.json'
    output_file = 'output.json'
    executable_opts = [f'--output={output_file}']

    @run_before('run')
    def set_parallel_resources(self):
        self.skip_if_no_procinfo()
        processor_info = self.current_partition.processor
        self.node_label = processor_info.arch
        if self.current_partition.devices:
            # device label, for example 4x-gpu-sm_80
            dev_label = ''
            for e in self.current_partition.devices:
                dev_label = f"-{dev_label}{e.num_devices}x-{e.type}-{e.arch}"

            self.node_label = self.node_label + dev_label

        # number of physical cores
        num_cores = int(
            processor_info.num_cpus / processor_info.num_cpus_per_core)

        self.ref_dict = (
            sirius_tests[self.test_name][self.node_label]
        )
        # total number of ranks
        self.num_tasks = self.ref_dict['performance_reference'][0]['R']
        # threads / rank
        T = self.ref_dict['performance_reference'][0]['T']
        self.num_cpus_per_task = T
        # ranks per node
        self.num_tasks_per_node = int(num_cores / T)
        if not self.env_vars:
            self.env_vars = {}
        self.env_vars['OMP_NUM_THREADS'] = '$SLURM_CPUS_PER_TASK'
        self.env_vars['OMP_PLACES'] = 'cores'
        self.env_vars['OMP_PROC_BIND'] = 'close'


    @run_after('setup')
    def set_test_dir(self):
        self.sourcesdir = self.test_name

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
class SARUS_sirius_scf_check(SIRIUSBase,
                             SarusExtraLauncherOptionsMixin,
                             CudaVisibleDevicesAllMixin):
    container_image = variable(str, type(None), value=None)
    valid_systems = ['+sarus']
    valid_prog_environs = ['builtin']

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
class UENV_sirius_scf_check(SIRIUSBase,
                            ExtraLauncherOptionsMixin,
                            CudaVisibleDevicesAllMixin):
    valid_systems = ['-amdgpu']
    valid_prog_environs = ['+sirius +mpi +openmp +uenv']
    tags = {'uenv', 'production', 'maintenance'}
