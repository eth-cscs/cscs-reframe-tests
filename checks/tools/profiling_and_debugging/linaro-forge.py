import os
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class linaro_ddt(rfm.RunOnlyRegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['+ddt']
    sourcesdir = None
    executable = 'ddt'
    rpt = variable(str, value='rpt.txt')
    env_vars = {
        # As explained in the documentation:
        # https://eth-cscs.github.io/alps-uenv/uenv-linaro-forge/
        # -> launch-the-code-with-the-debugger -> Warning note
        # in order to avoid "proxy type is invalid for this operation", we need
        'http_proxy': '"proxy.cscs.ch:8080"',
        'https_proxy': '"proxy.cscs.ch:8080"',
        'no_proxy': (
            r'".local, .cscs.ch, localhost, 148.187.0.0/16, 10.0.0.0/8, '
            r'172.16.0.0/12"'
        )
    }

    @run_before('run')
    def setup_ddt_flags(self):
        self.executable_opts = ['--offline', f'--output={self.rpt}', 'echo']

    @sanity_function
    def validate_solution(self):
        """
        Sanity checks:
         - "Error communicating with Licence Server velan.cscs.ch: The proxy
         type is invalid for this operation"
         - Offline log written to: 'rpt.txt'
         - message (0): Startup complete.
         - message (n/a): Every process in your program has terminated.
        """
        return sn.all([
            sn.assert_not_found(r'Error communicating with Licence Server',
                                self.stdout),
            sn.assert_found(
                rf"Offline log written to:.*{self.rpt}", self.stderr),
            sn.assert_found(r'Startup complete', self.rpt),
            sn.assert_found(
                r'Every process in your program has terminated', self.rpt),
        ])
