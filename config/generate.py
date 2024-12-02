# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import autopep8
import os
from jinja2 import Environment, FileSystemLoader
from utilities.config import SystemConfig
from utilities.io import getlogger, set_logger_level

JINJA2_TEMPLATE = 'reframe_config_template.j2'


def main(user_input, containers_search, devices_search, reservs,
         exclude_feat, access_opt, tmp_dir):

    # Initialize system configuration
    system_info = SystemConfig()
    # Build the configuration with the right options
    system_info.build_config(
        user_input=user_input, detect_containers=containers_search,
        detect_devices=devices_search, exclude_feats=exclude_feats,
        reservs=reservs, access_opt=access_opt, tmp_dir=tmp_dir
    )

    # Set up Jinja2 environment and load the template
    template_loader = FileSystemLoader(searchpath='.')
    env = Environment(loader=template_loader,
                      trim_blocks=True, lstrip_blocks=True)
    rfm_config_template = env.get_template(JINJA2_TEMPLATE)

    systemn_info_jinja = system_info.format_for_jinja()
    # Render the template with the gathered information
    organized_config = rfm_config_template.render(systemn_info_jinja)

    # Output filename for the generated configuration
    output_filename = f'{system_info.systemname}_config.py'

    # Format the content
    formatted = autopep8.fix_code(organized_config)

    # Overwrite the file with formatted content
    with open(output_filename, "w") as output_file:
        output_file.write(formatted)

    getlogger().info(
        f'\nThe following configuration files was created:\n'
        f'PYTHON: {system_info.systemname}_config.py', color=False
    )


if __name__ == '__main__':

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser()

    # Define the '--auto' flag
    parser.add_argument('--auto', action='store_true',
                        help='Turn off interactive mode')
    # Define the '--no-remote-containers' flag
    parser.add_argument(
        '--no-remote-containers', action='store_true',
        help='Disable container platform detection in remote partition'
    )
    # Define the '--no-remote-devices' flag
    parser.add_argument('--no-remote-devices', action='store_true',
                        help='Disable devices detection in remote partition')
    # Define the '--reservations' flag
    parser.add_argument(
        '--reservations', nargs='?',
        help='Specify the reservations that you want to create partitions for.'
    )
    # Define the '--exclude' flag
    parser.add_argument(
        '--exclude', nargs='?',
        help='Exclude the certain node features for the detection ' +
        'of node types'
    )
    # Define the '--prefix' flag
    parser.add_argument(
        '--prefix', action='store',
        help='Shared directory for remote detection jobs'
    )
    # Define the '--access' flag
    parser.add_argument(
        '--access', action='store',
        help='Compulsory options for accesing remote nodes with sbatch'
    )
    # Define the '--access' flag
    parser.add_argument(
        '-v', action='store_true',
        help='Set the verbosity to debug. Only effective if combined with --auto.'
    )

    args = parser.parse_args()

    user_input = not args.auto

    containers_search = True
    if args.no_remote_containers:
        containers_search = False

    devices_search = True
    if args.no_remote_devices:
        devices_search = False

    if args.reservations:
        reservs = args.reservations.split(',')
    else:
        reservs = False

    if args.exclude:
        exclude_feats = args.exclude.split(',')
    else:
        exclude_feats = []

    if args.prefix:
        if os.path.exists(args.prefix):
            tmp_dir = args.prefix
        else:
            raise ValueError('The specified d--prefix was not found')
    else:
        tmp_dir = []

    if args.access:
        access_opt = args.access.split(',')
    else:
        access_opt = ''

    user_input = not args.auto

    set_logger_level(args.v or user_input)

    main(user_input, containers_search, devices_search,
         reservs, exclude_feats, access_opt, tmp_dir)
