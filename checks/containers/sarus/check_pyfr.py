import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SarusPyFRCheck(rfm.RunOnlyRegressionTest):
    backend = parameter(['cuda', 'openmp'])
    sourcesdir = None
    valid_prog_environs = ['builtin']
    container_platform = 'Sarus'
    num_tasks = 1
    num_tasks_per_node = 1
    num_gpus_per_node = 1
    maintainers = ['amadonna', 'taliaga']
    tags = {'production'}

    @run_after('init')
    def set_valid_systems(self):
        if self.backend == 'cuda':
            self.valid_systems = ['dom:gpu', 'daint:gpu']
        else:
            self.valid_systems = ['dom:gpu', 'dom:mc', 'daint:gpu', 'daint:mc',
                                  'eiger:mc', 'pilatus:mc']

    @run_after('setup')
    def setup_container_platform(self):
        self.container_platform.image = ('ethcscs/pyfr:'
                                         '1.5.0-cuda8.0-ubuntu16.04')
        self.prerun_cmds = ['sarus --version']
        import_mesh_command = ('pyfr import ./euler_vortex_2d.msh '
                               './euler_vortex_2d.pyfrm')
        modify_ini_command = (
            r"sed -e 's/^;cblas.*/cblas = \/usr\/lib\/libopenblas.so/' "
            r"-i ./euler_vortex_2d.ini"
        )
        compute_command = (f'pyfr run --backend {self.backend} '
                           f'./euler_vortex_2d.pyfrm ./euler_vortex_2d.ini')
        self.container_platform.command = (
            f'bash -c "cd /PyFR-1.5.0/examples/euler_vortex_2d && '
            f'{import_mesh_command} && {modify_ini_command} && '
            f'{compute_command} && echo CHECK SUCCESSFUL"'
        )

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r'CHECK SUCCESSFUL', self.stdout)
