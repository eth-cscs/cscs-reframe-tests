# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import asyncio
import itertools
import logging
import sys
from typing import Union
from utilities.modules import ModulesSystem


async def status_bar():
    """
    Asynchronous function that displays a rotating status bar.
    """
    sys.stdout.write('\n')
    for symbol in itertools.cycle(["|", "/", "-", "\\"]):
        sys.stdout.write(f"\rWaiting for the submitted jobs... {symbol}")
        sys.stdout.flush()
        await asyncio.sleep(0.2)  # Adjust for desired speed of the status bar


class CustomFormatter(logging.Formatter):
    # Define ANSI escape codes for colors
    RESET = "\033[0m"
    COLORS = {
        logging.DEBUG: "",              # No color for DEBUG
        logging.INFO: "\033[32m",       # Green for INFO
        logging.WARNING: "\033[33m",    # Yellow for WARNING
        logging.ERROR: "\033[31m",      # Red for ERROR
        logging.CRITICAL: "\033[31;1m"  # Bright Red for CRITICAL
    }

    def format(self, record):
        # Check if the log has a 'color' attribute set for this message
        color = self.COLORS.get(record.levelno, self.RESET) if getattr(
            record, 'use_color', True) else ''
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


class CustomLogger(logging.Logger):
    def __init__(self):
        super().__init__("a")

        # Create console handler and formatter
        self.console_handler = logging.StreamHandler()
        formatter = CustomFormatter()
        self.console_handler.setFormatter(formatter)

        self.addHandler(self.console_handler)
        self.setLevel(logging.DEBUG)

    def _log_with_color(self, level, msg, *args, **kwargs):
        """Internal method to log with color control."""
        # Check if the user has passed the 'color' argument
        use_color = kwargs.pop('color', True)
        extra = kwargs.setdefault('extra', {})
        extra['use_color'] = use_color
        super()._log(level, msg, args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._log_with_color(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log_with_color(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log_with_color(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log_with_color(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._log_with_color(logging.CRITICAL, msg, *args, **kwargs)


_logger = CustomLogger()


def set_logger_level(debug_info: bool = True):
    global _logger
    if not debug_info:
        _logger.console_handler.setLevel(logging.INFO)


def getlogger():
    return _logger


def user_yn(prompt: str) -> bool:
    ''' Request user yes or no'''

    prompt = prompt + ' (y/n): '
    user_response = ''
    while user_response.lower() != 'y' and user_response.lower() != 'n':
        user_response = input(prompt)
    if user_response.lower() == 'y':
        return True
    else:
        return False


def user_integer(prompt: str, default_value: Union[int, None] = None) -> int:
    ''' Request user integer value'''

    if default_value:
        prompt = prompt + f' (default is {default_value}): '
    is_integer = False
    user_value = input(prompt)
    while not is_integer:
        if not user_value and default_value:
            return default_value
        try:
            user_value = int(user_value)
            is_integer = True
        except Exception:
            user_value = input('It must be an integer value:')

    return user_value


def user_selection(options: str, cancel_n: bool = False) -> Union[str, bool]:
    '''Request user selection from a list of options'''

    if cancel_n:
        msg = ('The selected option was not recognized. '
               'Please check the syntax (or press n to remove): ')
    else:
        msg = ('The selected option was not recognized. '
               'Please check the syntax: ')

    user_option = input('Please select one from the list above: ')
    while user_option not in options:
        user_option = input(msg)
        if cancel_n and user_option.lower() == 'n':
            return False

    return user_option


def user_descr(prompt: str, default_value: Union[str, None] = None,
               cancel_n: bool = False) -> Union[str, bool]:
    ''' Request user name / decription'''

    if default_value:
        prompt = prompt + f' (default is {default_value}): '
    elif cancel_n:
        prompt = prompt + ' (enter n to skip): '

    user_response = input(prompt)
    while not user_response:
        if default_value:
            return default_value
        user_response = input(prompt)
    if cancel_n and user_response.lower() == 'n':
        return False

    return user_response


def request_modules(modules_system: ModulesSystem) -> list:
    '''Request modules to be loaded'''

    modules_to_load = user_descr(
        'Do you require any modules to be loaded?\n'
        'Please write the modules names separated by commas',
        cancel_n=True
    )

    if modules_to_load:
        modules_to_load = [mod.strip() for mod in modules_to_load.split(',')]
        # Check that all the modules are available in the system
        check_modules = False
        while not check_modules:
            modules_ok = 0
            index_remove = []
            for m_i, module in enumerate(modules_to_load):
                new_module = ''
                # Check if the module system finds the requested module
                mod_options = modules_system.available_modules(module)
                if not mod_options:
                    new_module = user_descr(f'Module {module} not available.\n'
                                            'Specify the right one',
                                            cancel_n=True)
                elif len(mod_options) > 1:
                    # Several versions were detected
                    getlogger().debug(
                        'There are multiple versions of the '
                        f'module {module}: \n{mod_options}.\n'
                    )
                    new_module = user_selection(mod_options, cancel_n=True)
                    if new_module:
                        modules_ok += 1
                else:
                    modules_ok += 1

                if new_module:
                    modules_to_load[m_i] = new_module
                elif new_module != '':
                    index_remove.append(m_i)

            if len(modules_to_load) == modules_ok:
                check_modules = True
            elif len(modules_to_load) - len(index_remove) == modules_ok:
                for i in index_remove[::-1]:
                    modules_to_load.pop(i)
                check_modules = True
            else:
                for i in index_remove[::-1]:
                    modules_to_load.pop(i)

    return modules_to_load
