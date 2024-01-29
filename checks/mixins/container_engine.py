# Copyright 2016-2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.typecheck as typ


class ContainerEngineMixin(rfm.RegressionMixin):
    #: The container image to use.
    #:
    #: :default: ``required``
    container_image = variable(str)

    #: The working directory of the container.
    #:
    #: :default: ``'/rfm_workdir/'``
    container_workdir = variable(str, value='/rfm_workdir')

    #: A list of the container mounts following the <src dir>:<target dir>
    #: convention.
    #: The test stage directory is always mounted on `/rfm_workdir`.
    #:
    #: :default: ``[]``
    container_mounts = variable(typ.List[str], value=[])

    @run_after('setup')
    def create_env_file(self):
        mounts = ',\n'.join(f'"{m}"' for m in self.container_mounts)
        toml_lines = [
            f'image = "{self.container_image}"',
            f'mounts = [',
            f'"{self.stagedir}:/rfm_workdir",',
            mounts,
            f']',
            f'workdir = "{self.container_workdir}"'
        ]

        self.env_file = f'{self.stagedir}/rfm_env.toml'
        with open(self.env_file, 'w') as f:
            f.write('\n'.join(l for l in toml_lines if l))

    @run_before('run')
    def set_container_engine_env_launcher_options(self):
        self.job.launcher.options += [f'--environment={self.env_file}']
