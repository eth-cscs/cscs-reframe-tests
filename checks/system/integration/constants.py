# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#

# Package names
pkg_names = {'bubblewrap': ['bwrap'],
             'ltrace': ['ltrace'],
             'gcc12': ['gcc-12'],
             'nnn': ['nnn'],
             'netcat': ['netcat'],
             'lua-lmod': ['lua'],
             'pycxi-utils': ['cxi_stat', 'cxi_atomic_bw',
                             'cxi_atomic_lat', 'cxi_gpu_loopback_bw',
                             'cxi_healthcheck', 'cxi_heatsink_check',
                             'cxi_read_bw', 'cxi_read_lat',
                             'cxi_send_bw', 'cxi_send_lat',
                             'cxi_write_lat', 'cxi_write_bw'],
             'gcc12-fortran': ['gfortran-12'],
             'datacenter-gpu-manager': ['dcgmi'],
             'ansible': ['ansible'],
             'gcc12-c++': ['g++-12'],
             'fuse3': ['mount', 'adduser', 'libc6', 'libfuse3-3',
                       'sed'],
             'libtool': ['libtool'],
             'wget': ['wget'],
             'htop': ['htop'],
             'lsof': ['lsof'],
             'lbcd': ['lbcdclient']
             }

tools_installation = {'fakerootuidsync': '/usr/sbin/fakerootuidsync',
                      }

json_file_path = '../systems_data'

MOUNT_VARS   = ['filesystems',
                'capstor_scratch_cscs_path',
                'capstor_store_cscs_path',
                'capstor_users_cscs_path',
                'iopsstor_scratch_cscs_path',
                'iopsstor_store_cscs_path']

TOOLS_VARS   = ['cscs_cluster_extra_pkgs', 'cscs_platform_packages']
ENV_VARS     = 'cscs_extra_vars'
PROXY_VARS   = {'proxy_server': 'proxy_server',
                'proxy_port': 'proxy_port',
                'no_proxy': 'no_proxy'}

VSERVICES_DICT = {'v-cluster': 'vcluster',
                  'storage': 'storage'}
