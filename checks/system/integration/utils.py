# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# Definition of Check class and function.
#


class Check:

    #
    # This is a singleton value for a running counter of the number of checks
    # we have created.
    #
    check_id = 0

    def __init__(self):
        #
        # These can to be defined by the user:
        #

        # Name for the class of check we are creating.
        self.CLASS         = 'NOCLASS'
        # Print what check will be created. Do nothing.
        self.DEBUG         = False
        # The computing system we expect to run on.
        self.SYSTEM        = None
        # The name of the calling module. Should be set from the caller.
        self.MODULE_NAME   = __name__

    def __call__(self, cmd, expected=None, not_expected=None, where=''):
        """
        Create a test of 'cmd'. A regex describing the expected output

        :param cmd:             The command and its arguments to execute. This
                                may include shell pipes and redirections.
        :param expected:        A string or [string,string]. In the first case,
                                string is a regular expression describing the
                                expected output.  In the second case, the
                                first string is the regex and the second string
                                is either 'stdout' or 'stderr', depending on
                                where the regex should search. The default is
                                'stdout'.  If None, or missing, no search will
                                be performed.
        :param not_expected:    Similar to 'expected', but what should not be
                                found.
        """

        def debuginfo():
            """
            To help the user, grab the line where this check was created
            from so we can include it in any error message.
            """
            from inspect import getframeinfo, stack
            caller = getframeinfo(stack()[2][0])
            return "[%s:%d]" % (caller.filename, caller.lineno)

        #
        # We intentionally increment here before the inclusion/exclusion tests
        # so that numbering stays consistent when all tests are enabled.
        #
        Check.check_id += 1

        #
        # If where is unspecificed we can run with any feature.
        # Be forgiving if the user forgets a leading +.
        #

        if not where:
            where = ['*']
        else:
            where = where.split()
            if len(where) > 1:
                for i, item in enumerate(where):
                    if item[0] not in ['-', '+']:
                        where[i] = f"+{where[i]}"
                where = [" ".join(where)]
            else:
                if where[0][0] not in ['-', '+']:
                    where[0] = f'+{where[0]}'

        #
        # Get our properties ready.
        #

        name                = f'Check_{Check.check_id:04}_{self.CLASS}'
        tag                 = f'sysint-{self.CLASS}'
        valid_systems       = where
        valid_prog_environs = ['builtin']
        time_limit          = '2m'

        if self.DEBUG:
            exp_str, nexp_str = '', ''
            if expected is not None:
                exp_str  = f"expected:{expected}"
            if not_expected is not None:
                nexp_str = f"not_expected:{not_expected}"

            print(f"{debuginfo()} {name:25} {cmd:80} -> {exp_str} {nexp_str}" +
                  (f"  on  {valid_systems} with {valid_prog_environs}"))
            return

        #
        # Wait until here to do any imports so that if we are running in debug
        # mode we don't depend on the ReFrame framework being present.
        #

        import reframe as rfm
        import reframe.utility.sanity as sn
        import reframe.core.builtins as builtins

        from reframe.core.meta import make_test

        def validate(test):
            """Callback to check that we got the output we expected."""

            a, b = True, True

            expected, where = test.expected
            if expected is not None:
                where = eval(f'test.{test.expected[1]}')
                a = sn.assert_found(
                    expected,
                    where,
                    msg=f"Expected '{expected}' running " +
                        f"'{test.cmd} {test.caller}'")

            not_expected, where = test.not_expected
            if not_expected is not None:
                where = eval(f'test.{test.not_expected[1]}')
                b = sn.assert_not_found(
                    not_expected,
                    where,
                    msg=f"Did not expect '{not_expected}' " +
                        f"running '{test.cmd} {test.caller}'")
            return (a and b)

        def set_command_options(test):
            """Set up the options we need to run"""

            test.executable = test.cmd

            if isinstance(test.expected, list):
                test.expected = test.expected
            else:
                test.expected = [test.expected, 'stdout']

            if isinstance(test.not_expected, list):
                test.not_expected = test.not_expected
            else:
                test.not_expected = [test.not_expected, 'stdout']

            test.skip_if(
                test.expected[1] not in ['stdout', 'stderr'],
                msg=f'Location for expected ' +
                    f'is not stdout or stderr {test.caller}')

            test.skip_if(
                test.not_expected[1] not in ['stdout', 'stderr'],
                msg=f'Location for not_expected ' +
                    f'is not stdout or stderr {test.caller}')

        def check_system(test):
            """Check that the system we require is the system we are on,
            otherwise skip the test."""

            test.skip_if(
                test.current_system.name != self.SYSTEM,
                msg=f'Required sytem {self.SYSTEM} ' +
                    f'but found {test.current_system.name}.')

        #
        # Finally, create and register the test.
        #
        t = make_test(
            name,
            (rfm.RunOnlyRegressionTest,),
            {
                'cmd': cmd,
                'expected': expected,
                'not_expected': not_expected,
                'valid_systems': valid_systems,
                'valid_prog_environs': valid_prog_environs,
                'time_limit': time_limit,
                'caller': debuginfo(),
                'tags': {'production', tag},
            },
            [
                builtins.run_after('setup')(set_command_options),
                builtins.run_after('init')(check_system),
                builtins.sanity_function(validate),
            ],
            module=self.MODULE_NAME
        )
        rfm.simple_test(t)
