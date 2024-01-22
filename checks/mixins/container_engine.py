# Copyright 2016-2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm


class ContainerEngineMixin(rfm.RegressionMixin):
    @run_after('setup')
    def create_env_file(self):
        self.env_file = f'{self.stagedir}/rfm_env.toml'
        toml_lines = [
            f'image = "{self.image}"',
            f'mounts = [',
            f'"{self.stagedir}:/rfm_workdir"',
            f']',
            f'workdir = "/rfm_workdir"'
        ]
        with open(self.env_file, 'w') as f:
            f.write('\n'.join(toml_lines))

    @run_before('run')
    def set_container_engine_env_launcher_options(self):
        self.job.launcher.options += [f'--environment={self.env_file}']
