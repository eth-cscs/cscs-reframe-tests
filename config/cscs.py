# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#
import os
from reframe.utility import import_module_from_file

systems = ['common', 'ault', 'daint', 'eiger', 'hohgant']
# TDS systems are already included in the production systems,
# for example dom is included in the daint configuration file
config_files = [
    os.path.join(os.path.dirname(__file__), f"{sys}.py") for sys in systems
]
# print(config_files)
system_configs = [
    import_module_from_file(f).site_configuration for f in config_files
]

site_configuration = {}
for c in system_configs:
    for key, val in c.items():
        site_configuration.setdefault(key, [])
        site_configuration[key] += val
