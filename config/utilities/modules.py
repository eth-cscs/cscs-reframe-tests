# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import abc
import os
import re
import subprocess


class ModulesSystem(abc.ABC):
    '''Abstract base class for module systems.

    :meta private:
    '''

    @abc.abstractmethod
    def _execute(self, cmd: str, *args):
        '''Execute an arbitrary command of the module system.'''

    @abc.abstractmethod
    def available_modules(self, substr: str):
        '''Return a list of available modules, whose name contains ``substr``.

        This method returns a list of Module instances.
        '''
    @property
    @abc.abstractmethod
    def name(self):
        '''Return the name of this module system.'''

    @property
    @abc.abstractmethod
    def version(self):
        '''Return the version of this module system.'''

    @abc.abstractmethod
    def modulecmd(self, *args):
        '''The low level command to use for issuing module commads'''


class TMod32Impl(ModulesSystem):
    '''Base class for TMod Module system (Tcl).'''

    MIN_VERSION = (3, 2)

    def __init__(self):
        self._version = None
        self.found = self._do_validate()

    def _do_validate(self) -> bool:
        # Try to figure out if we are indeed using the TCL version
        try:
            completed = subprocess.run(
                ['modulecmd', '-V'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True, check=True
            )
        except Exception:
            return False

        version_match = re.search(r'^VERSION=(\S+)', completed.stdout,
                                  re.MULTILINE)
        tcl_version_match = re.search(r'^TCL_VERSION=(\S+)', completed.stdout,
                                      re.MULTILINE)

        if version_match is None or tcl_version_match is None:
            return False

        version = version_match.group(1)
        try:
            ver_major, ver_minor = [int(v) for v in version.split('.')[:2]]
        except ValueError:
            return False

        if (ver_major, ver_minor) < self.MIN_VERSION:
            return False

        self._version = version

        return True

    @property
    def name(self) -> str:
        return 'tmod32'

    @property
    def version(self) -> str:
        return self._version

    def modulecmd(self, *args) -> str:
        return ['modulecmd', 'python', *args]

    def _execute(self, cmd: str, *args) -> str:

        modulecmd = self.modulecmd(cmd, *args)
        completed = subprocess.run(
            modulecmd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, check=True
        )
        if re.search(r'\bERROR\b', completed.stderr) is not None:
            return ''

        return completed.stderr

    def available_modules(self, substr: str) -> list:
        output = self._execute('avail', '-t', substr)
        ret = []
        for line in output.split('\n'):
            if not line or line[-1] == ':':
                # Ignore empty lines and path entries
                continue

            module = re.sub(r'\(default\)', '', line)
            ret.append(module)

        return ret


class TMod31Impl(TMod32Impl):
    '''Module system for TMod (Tcl).'''

    MIN_VERSION = (3, 1)

    def __init__(self):
        self._version = None
        self._command = None
        self.found = self._do_validate()

    def _do_validate(self) -> bool:
        # Try to figure out if we are indeed using the TCL version
        try:
            modulecmd = os.getenv('MODULESHOME')
            modulecmd = os.path.join(modulecmd, 'modulecmd.tcl')
            completed = subprocess.run(
                [modulecmd],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True, check=True)
        except OSError:
            return False

        version_match = re.search(r'Release Tcl (\S+)', completed.stderr,
                                  re.MULTILINE)
        tcl_version_match = version_match

        if version_match is None or tcl_version_match is None:
            return False

        version = version_match.group(1)
        try:
            ver_major, ver_minor = [int(v) for v in version.split('.')[:2]]
        except ValueError:
            return False

        if (ver_major, ver_minor) < self.MIN_VERSION:
            return False

        self._version = version
        self._command = f'{modulecmd} python'

        return True

    @property
    def name(self) -> str:
        return 'tmod31'

    def modulecmd(self, *args):
        return [self._command, *args]

    def _execute(self, cmd: str, *args) -> str:

        modulecmd = self.modulecmd(cmd, *args)
        completed = subprocess.run(
            modulecmd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, check=True
        )
        if re.search(r'\bERROR\b', completed.stderr) is not None:
            return ''

        exec_match = re.search(r"^exec\s'(\S+)'", completed.stdout,
                               re.MULTILINE)

        with open(exec_match.group(1), 'r') as content_file:
            cmd = content_file.read()

        return completed.stderr


class TMod4Impl(TMod32Impl):
    '''Module system for TMod 4.'''

    MIN_VERSION = (4, 1)

    def __init__(self):
        self._version = None
        self._extra_module_paths = []
        self.found = self._do_validate()

    def _do_validate(self):
        try:
            completed = subprocess.run(
                self.modulecmd('-V'),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True, check=True
            )
        except Exception:
            return False

        version_match = re.match(r'^Modules Release (\S+)\s+',
                                 completed.stderr)
        if not version_match:
            return False

        version = version_match.group(1)
        try:
            ver_major, ver_minor = [int(v) for v in version.split('.')[:2]]
        except ValueError:
            return False

        if (ver_major, ver_minor) < self.MIN_VERSION:
            return False

        self._version = version
        return True

    @property
    def name(self) -> str:
        return 'tmod4'

    def modulecmd(self, *args) -> list:
        return ['modulecmd', 'python', *args]

    def _execute(self, cmd: str, *args) -> str:

        modulecmd = self.modulecmd(cmd, *args)
        completed = subprocess.run(
            modulecmd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, check=True
        )
        namespace = {}

        # _mlstatus is set by the TMod4 only if the command was unsuccessful,
        # but Lmod sets it always
        if not namespace.get('_mlstatus', True):
            return ''

        return completed.stderr


class LModImpl(TMod4Impl):
    '''Module system for Lmod (Tcl/Lua).'''

    def __init__(self):
        self._extra_module_paths = []
        self._version = None
        self.found = self._do_validate()

    def _do_validate(self) -> bool:
        # Try to figure out if we are indeed using LMOD
        self._lmod_cmd = os.getenv('LMOD_CMD')
        if self._lmod_cmd is None:
            return False

        try:
            completed = subprocess.run(
                [f'{self._lmod_cmd}', '--version'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True, check=True
            )
        except Exception:
            return False

        version_match = re.search(r'.*Version\s*(\S+)', completed.stderr,
                                  re.MULTILINE)
        if version_match is None:
            return False

        self._version = version_match.group(1)
        # Try the Python bindings now
        completed = subprocess.run(
            self.modulecmd(),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, check=False
        )
        if '_mlstatus' not in completed.stdout:
            return False

        if re.search(r'Unknown shell type', completed.stderr):
            return False

        return True

    @property
    def name(self) -> str:
        return 'lmod'

    def modulecmd(self, *args) -> list:
        return [self._lmod_cmd, 'python', *args]

    def available_modules(self, substr: str) -> list:
        output = self._execute('-t', 'avail', substr)
        ret = []
        for line in output.split('\n'):
            if not line or line[-1] == ':':
                # Ignore empty lines and path entries
                continue

            module = re.sub(r'\(\S+\)', '', line)
            ret.append(module)

        return ret


modules_impl = {
    'tmod31': TMod31Impl,
    'tmod32': TMod32Impl,
    'tmod4': TMod4Impl,
    'lmod': LModImpl,
}
