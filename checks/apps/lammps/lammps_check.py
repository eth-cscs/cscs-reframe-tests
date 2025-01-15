import os

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
import uenv


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