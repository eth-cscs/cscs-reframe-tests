# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#

# Package names
pkg_names = {"bubblewrap"             : "bwrap",
             "ltrace"                 : "ltrace",
             "gcc12"                  : "gcc-12",
             "nnn"                    : "nnn",
             "netcat"                 : "nc",
             "lua-lmod"               : "lmod",
             "pycxi-utils"            : "cx",
             "gcc12-fortran"          : "gfortran-12",
             "datacenter-gpu-manager" : "dcgmi",
             "ansible"                : "ansible",
             "gcc12-c++"              : "g++-12"}

yaml_files_path = "/users/bfuentes/sandbox/"

MOUNT_VARS = "filesystems"
TOOLS_VARS = "cscs_cluster_extra_pkgs"