# Copyright 2016-2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm

from reframe.core.exceptions import SkipTestError


class ContainerEngineMixin(rfm.RegressionMixin):
    @run_after('setup')
    def create_env_file(self):
        try:
            image = self.container_image
        except AttributeError: 
            raise SkipTestError('a valid container image has to be defined')

        try:
            workdir = self.workdir
        except AttributeError: 
            workdir = "rfm_workdir"

        try:
            mounts = ',\n'.join(self.container_mounts)
        except AttributeError: 
            mounts = '' 

        toml_lines = [
            f'image = "{image}"',
            f'mounts = [',
            f'"{self.stagedir}:/rfm_workdir"',
            mounts,
            f']',
            f'workdir = "{workdir}"'
        ]

        self.env_file = f'{self.stagedir}/rfm_env.toml'
        with open(self.env_file, 'w') as f:
            f.write('\n'.join(l for l in toml_lines if l))

    @run_before('run')
    def set_container_engine_env_launcher_options(self):
        self.job.launcher.options += [f'--environment={self.env_file}']
