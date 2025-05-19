import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class uenv_status(rfm.RunOnlyRegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['*']
    local = True
    executable = 'uenv status'
    tags = {'uenv', 'vs-node-validator'}

    @sanity_function
    def validate(self):
        return sn.assert_found(r'there is no uenv loaded', self.stdout)

