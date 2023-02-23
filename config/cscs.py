# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#
import glob
import os
from reframe.utility import import_module_from_file


system_conf_files = glob.glob(
    os.path.join(os.path.dirname(__file__), 'systems', '*.py')
)
config_files = [
    os.path.join(os.path.dirname(__file__), 'common.py')
]
# Filter out the links
config_files += [s for s in system_conf_files if not os.path.islink(s)]
system_configs = [
    import_module_from_file(f).site_configuration for f in config_files
]

site_configuration = {}
for c in system_configs:
    for key, val in c.items():
        site_configuration.setdefault(key, [])
        site_configuration[key] += val
