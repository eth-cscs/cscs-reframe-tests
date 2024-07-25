# ----------------------------------------------------------------------------#
#                                                                             #
# Definition of Check class and function                                      #
#                                                                             #
# ----------------------------------------------------------------------------#

class Check:

    CLASS = ''
    CLASS_EXCLUDE = []
    CLASS_INCLUDE = []
    DEBUG = False
    SYSTEM = None

    def __call__(self, cmd, expected=None, not_expected=None, where='', check_count=[0]):
        """
        Create a test of 'cmd'. A regex describing the expected output

        :param cmd:    The command and its arguments to execute. This may include
                       shell pipes and redirections.
        :param expected: A string or [string,string]. In the first case, string
                       is a regular expression describing the expected output.
                       In the second case, the first string is the regex and the
                       second string is either 'stdout' or 'stderr', depending on 
                       where the regex should search. The default is 'stdout'.
                       If None, or missing, no search will be performed.
        :param not_expected: Similar to 'expected', but what should not be found.
        """

        check_count[0] += 1

        lcl_CHECK_CLASS = ''
        if self.CLASS:
            lcl_CHECK_CLASS = f'_{self.CLASS}'

        if '*' not in self.CLASS_EXCLUDE:
            if self.CLASS in self.CLASS_EXCLUDE:
                return
        else:
            if '*' not in self.CLASS_INCLUDE:
                if self.CLASS not in self.CLASS_INCLUDE:
                    return

        if where and where[0] not in ['-', '+']:
            where = f'+{where}'

        name                = f'Check_{check_count[0]:04}{lcl_CHECK_CLASS}'
        valid_systems       = [self.SYSTEM] + where.split()
        valid_prog_environs = ['builtin']
        time_limit          = '2m'

        if self.DEBUG:
            print(   f"{name:25} {cmd:80} -> "
                  + (f"expected:{expected}"           if expected     is not None else '') 
                  + (f"not_expected:{not_expected}"   if not_expected is not None else '') 
                  + (f"  on  {valid_systems} with {valid_prog_environs}"))
            return

        import reframe.utility.sanity as sn
        import reframe.core.builtins as builtins

        from reframe.core.meta import make_test


        def validate(test):
            def v0(ex):
                nonlocal test
                e,w = ex if isinstance(ex, list) else [ex, 'stdout']
                assert w in ['stdout', 'stderr']
                return [e, eval(f'test.{w}')]

            a,b = True,True
            expected, where = v0(test.expected)
            if expected is not None:
                msg = f"Expected '{expected}' running '{test.cmd}'"
                a = sn.assert_found(expected, where, msg=msg)

            not_expected, where = v0(test.not_expected)
            if not_expected is not None:
                msg = f"Did not expect '{not_expected}' running '{test.cmd}'"
                b = sn.assert_not_found(not_expected, where, msg=msg)
            return (a and b) 

        def set_executable_opts(test):
            test.executable = test.cmd
            #test.executable, *test.executable_opts = test.cmd.split()

        t = make_test(
                f'Check_{check_count[0]:04}{lcl_CHECK_CLASS}', 
                (rfm.RunOnlyRegressionTest,),
                {'cmd': cmd,
                 'expected': expected,
                 'not_expected': not_expected,
                 'valid_systems': valid_systems,
                 'valid_prog_environs': valid_prog_environs,
                 'time_limit': time_limit,
                },
                [builtins.run_before('run')(set_executable_opts),
                 builtins.sanity_function(validate),
                ]
            )
        rfm.simple_test(t)

check = Check()
