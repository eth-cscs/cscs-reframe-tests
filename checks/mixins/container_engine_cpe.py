# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.typecheck as typ


class ContainerEngineMixinCPE(rfm.RegressionMixin):
    #: The container image to use.
    #:
    #: :default: ``required``
    container_image = variable(str)

    #: The working directory of the container.
    #:
    #: Setting to `None` will not set any workdir for the container
    #:
    #: :default: ``'/rfm_workdir/'``
    container_workdir = variable(str, type(None), value='/rfm_workdir')

    #: A list of the container mounts following the <src dir>:<target dir>
    #: convention.
    #: The test stage directory is always mounted on `/rfm_workdir`.
    #:
    #: :default: ``[]``
    container_mounts = variable(typ.List[str], value=[])

    #: A dictionary of key/values to pass to the container environment.
    #:
    #: :default: ``{}``
    container_env_key_values = variable(typ.Dict[str, str], value={})

    #: A dictionary of tables to pass to the container environment.
    #: For each key, a dictionary of key/value pairs is given.
    #:
    #: :default: ``{}``
    container_env_table= variable(typ.Dict[str, typ.Dict[str, str]], value={})

    @run_before('compile')
    def create_env_file(self):
        mounts = ',\n'.join(f'"{m}"' for m in self.container_mounts)
        toml_lines = [
            f'image = "{self.container_image}"',
            f'mounts = [',
            f'"{self.stagedir}:/rfm_workdir",',
            f'"{self.stagedir}:{self.stagedir}",',
            mounts,
            f']',
        ]
        toml_lines += [f'workdir = "{self.stagedir}"']

        for k, v in self.container_env_key_values.items():
            toml_lines.append(f'{k} = "{v}"')

        for table_name, values in self.container_env_table.items():
            if values:
                toml_lines.append(f'[{table_name}]')
                for k, v in values.items():
                    toml_lines.append(f'{k} = "{v}"')

        self.env_file = f'{self.stagedir}/rfm_env.toml'
        with open(self.env_file, 'w') as f:
            f.write('\n'.join(l for l in toml_lines if l))

    @run_before('compile')
    def set_sbatch(self):
        self.build_job.options += [f'--environment={self.env_file}']

    @run_before('run')
    def set_container_engine_env_launcher_options(self):
        self.job.options += [f'--environment={self.env_file}']
