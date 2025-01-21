import os

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
import uenv

slurm_config = {
    "lammps+gpu-lj": {
        "gh200": {
            "nodes": 2,
            "ntasks-per-node": 32,
            "walltime": "0d0h20m0s",
            "gpu": True,
        },
    },
}

class lammps_download(rfm.RunOnlyRegressionTest):
    '''
    Download LAMMPS source code.
    '''

    version = variable(str, value='20230802.3')
    descr = 'Fetch LAMMPS source code'
    sourcedir = None
    executable = 'wget'
    executable_opts = [
        '--quiet',
        'https://download.lammps.org/tars/lammps-2Aug2023.tar.gz',
        '-O',
        f'LAMMPS_{version}_Source.tar.gz',
    ]
    local = True

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class LAMMPSBuildTest(rfm.CompileOnlyRegressionTest):
    '''
    Test LAMMPS build from source.
    # lammps:develop-gpu
    # lammps:develop-kokkos
    # lammps:gpu
    # lammps:kokkos
    # lammps:spack
    '''
    descr = 'LAMMPS Build Test'
    valid_prog_environs = ['+lammps-kokkos-dev']
    valid_systems = ['*']
    maintainers = ['SSA']
    lammps_sources = fixture(lammps_download, scope='session')
    build_system = 'CMake'
    tags = {'uenv'}
    build_locally = False

    @run_before('compile')
    def prepare_build(self):
        #self.job.launcher.options = ['--uenv=/capstor/scratch/cscs/browning/images/lammps.squashfs']
        self.extra_resources = {"gres": {"gpu": 4}}
        self.uarch = uenv.uarch(self.current_partition)
        self.skip_if_no_procinfo()
        cpu = self.current_partition.processor
        self.build_system.builddir = os.path.join(self.stagedir, 'build')
        self.build_system.config_opts = [
            f'-C {self.stagedir}/lammps-2Aug2023/cmake/presets/kokkos-cuda.cmake',
            f'{self.stagedir}/lammps-2Aug2023/cmake/',
            '-DKokkos_ENABLE_IMPL_CUDA_MALLOC_ASYNC=OFF',
            '-DKokkos_ARCH_NATIVE=ON',
            '-DKokkos_ARCH_PASCAL60=OFF',
            '-DKokkos_ARCH_HOPPER90=ON',
        ]
        self.build_system.max_concurrency = 64

        tarsource = os.path.join(
            self.lammps_sources.stagedir,
            f'LAMMPS_{self.lammps_sources.version}_Source.tar.gz',
        )

        # Extract source code
        self.prebuild_cmds = [
            f'tar -xzf {tarsource} -C {self.stagedir}',
        ]

    @sanity_function
    def validate_test(self):
        self.lammps_executeable = os.path.join(self.stagedir, "build",
                                               "lmp")
        return os.path.isfile(self.lammps_executeable)
    
class LammpsGPUCheck(rfm.RunOnlyRegressionTest):
    executable = './mps-wrapper.sh lmp'
    valid_prog_environs = ['+lammps-gpu-prod']
    maintainers = ["SSA"]
    valid_systems = ["*"]
    test_name = "lammps+gpu-lj"
    executable_opts = ["-i", "lj.in"]
    energy_reference = -4.620456

    @run_before("run")
    def prepare_run(self):
        self.uarch = uenv.uarch(self.current_partition)
        config = slurm_config[self.test_name][self.uarch]
        # sbatch options
        self.extra_resources = {"gres": {"gpu": 4}}
        self.job.options = [
            f'--nodes={config["nodes"]}',
        ]
        self.num_tasks_per_node = config["ntasks-per-node"]
        self.num_tasks = config["nodes"] * self.num_tasks_per_node
        self.ntasks_per_core = 1
        self.time_limit = config["walltime"]

        # environment variables
        if self.uarch == "gh200":
            self.env_vars["MPICH_GPU_SUPPORT_ENABLED"] = "1"

    @sanity_function
    def assert_energy_diff(self):
        energy = sn.extractsingle(
            r"^\s*1000\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(-?\d+\.\d+)",
            self.stdout,
            "energy",
            float,
            item=-1,
        )
        energy_diff = sn.abs(energy - self.energy_reference)
        successful_termination = sn.assert_found(r"Total wall time", self.stdout)
        correct_energy = sn.assert_lt(energy_diff, 1e-4)
        return sn.all(
            [
                successful_termination,
                correct_energy,
            ]
        )

    # INFO: The name of this function needs to match with the reference dict!
    #@performance_function("s")
    #def time_run(self):
        #return sn.extractsingle(r'electrons.+\s(?P<wtime>\S+)s WALL',
        #                        self.stdout, 'wtime', float)
        #pass
    
       
    