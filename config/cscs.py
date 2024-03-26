# Copyright 2016 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#
import glob
import os
import sys
from reframe.utility import import_module_from_file

base_dir = os.path.dirname(os.path.abspath(__file__))
utilities_path = os.path.join(base_dir, 'utilities')
sys.path.append(utilities_path)

import firecrest_slurm


firecrest = os.environ.get('RFM_FIRECREST', None)
uenv = os.environ.get('UENV', None)

def is_var_true(var):
    if var is None:
        return False

    return var.lower() in ['true', 'yes', '1']

systems_path = 'systems-firecrest' if is_var_true(firecrest) else 'systems-uenv' if is_var_true(uenv) else 'systems'

system_conf_files = glob.glob(
    os.path.join(os.path.dirname(__file__), systems_path, '*.py')
)
config_files = [
    os.path.join(os.path.dirname(__file__), 'common.py')
]
# Filter out the links
config_files += [s for s in system_conf_files if not os.path.islink(s)]
system_configs = [
    import_module_from_file(f).site_configuration for f in config_files
]

# Build the configuration dictionary from all the systems/*.py config files
site_configuration = {}
for c in system_configs:
    for key, val in c.items():
        site_configuration.setdefault(key, [])
        site_configuration[key] += val
