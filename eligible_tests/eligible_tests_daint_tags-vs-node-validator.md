## Eligible ReFrame Tests on daint

- Filters:
  - system: `daint`
  - tags: `vs-node-validator`
  - checks: `25`
- Generated: `2026-05-13 17:01:26 +0200`

| Test name | Description | Category |
|----------|-------------|----------|
| [DcgmRpmCheck](../checks/system/gssr/dcgm_hook.py) | Check DCGM executable and libraries are installed | [system/gssr](../checks/system/gssr/) |
| [GssrCeHookCheck](../checks/system/gssr/dcgm_hook.py)<br>• %pytorch_image_tag=25.01-py3_nvrtc-12.9 | Check DCGM CE hook is working with gssr | [system/gssr](../checks/system/gssr/) |
| [MountPointExistsTest 'lustre')](../checks/system/integration/v-cluster_config.py)<br>• %mount_info=('capstor/scratch/cscs', | Test mount points in the system | [system/integration](../checks/system/integration/) |
| [MountPointExistsTest 'lustre')](../checks/system/integration/v-cluster_config.py)<br>• %mount_info=('capstor/store/cscs', | Test mount points in the system | [system/integration](../checks/system/integration/) |
| [MountPointExistsTest 'lustre')](../checks/system/integration/v-cluster_config.py)<br>• %mount_info=('iopsstor/scratch/cscs', | Test mount points in the system | [system/integration](../checks/system/integration/) |
| [MountPointExistsTest 'lustre')](../checks/system/integration/v-cluster_config.py)<br>• %mount_info=('iopsstor/store/cscs', | Test mount points in the system | [system/integration](../checks/system/integration/) |
| [MountPointExistsTest 'nfs')](../checks/system/integration/v-cluster_config.py)<br>• %mount_info=('/users', | Test mount points in the system | [system/integration](../checks/system/integration/) |
| [PackagePresentTest](../checks/system/integration/v-cluster_config.py)<br>• %tools_info=netcat | Test pkgs installation in the system | [system/integration](../checks/system/integration/) |
| [PackagePresentTest](../checks/system/integration/v-cluster_config.py)<br>• %tools_info=gcc12-fortran | Test pkgs installation in the system | [system/integration](../checks/system/integration/) |
| [PackagePresentTest](../checks/system/integration/v-cluster_config.py)<br>• %tools_info=htop | Test pkgs installation in the system | [system/integration](../checks/system/integration/) |
| [PackagePresentTest](../checks/system/integration/v-cluster_config.py)<br>• %tools_info=lsof | Test pkgs installation in the system | [system/integration](../checks/system/integration/) |
| [PackagePresentTest](../checks/system/integration/v-cluster_config.py)<br>• %tools_info=libtool | Test pkgs installation in the system | [system/integration](../checks/system/integration/) |
| [PackagePresentTest](../checks/system/integration/v-cluster_config.py)<br>• %tools_info=ltrace | Test pkgs installation in the system | [system/integration](../checks/system/integration/) |
| [PackagePresentTest](../checks/system/integration/v-cluster_config.py)<br>• %tools_info=ansible | Test pkgs installation in the system | [system/integration](../checks/system/integration/) |
| [PackagePresentTest](../checks/system/integration/v-cluster_config.py)<br>• %tools_info=bubblewrap | Test pkgs installation in the system | [system/integration](../checks/system/integration/) |
| [PackagePresentTest](../checks/system/integration/v-cluster_config.py)<br>• %tools_info=nnn | Test pkgs installation in the system | [system/integration](../checks/system/integration/) |
| [PackagePresentTest](../checks/system/integration/v-cluster_config.py)<br>• %tools_info=wget | Test pkgs installation in the system | [system/integration](../checks/system/integration/) |
| [PackagePresentTest](../checks/system/integration/v-cluster_config.py)<br>• %tools_info=pycxi-utils | Test pkgs installation in the system | [system/integration](../checks/system/integration/) |
| [PackagePresentTest](../checks/system/integration/v-cluster_config.py)<br>• %tools_info=datacenter-gpu-manager | Test pkgs installation in the system | [system/integration](../checks/system/integration/) |
| [PackagePresentTest](../checks/system/integration/v-cluster_config.py)<br>• %tools_info=gcc12-c++ | Test pkgs installation in the system | [system/integration](../checks/system/integration/) |
| [PackagePresentTest](../checks/system/integration/v-cluster_config.py)<br>• %tools_info=lua-lmod | Test pkgs installation in the system | [system/integration](../checks/system/integration/) |
| [PackagePresentTest](../checks/system/integration/v-cluster_config.py)<br>• %tools_info=gcc12 | Test pkgs installation in the system | [system/integration](../checks/system/integration/) |
| [EnvVariableConfigTest '/capstor/apps/cscs/daint')](../checks/system/integration/v-cluster_config.py)<br>• %envs_info=('APPS', | Test environment variables of the system | [system/integration](../checks/system/integration/) |
| [EnvVariableConfigTest '/capstor/scratch/cscs/')](../checks/system/integration/v-cluster_config.py)<br>• %envs_info=('SCRATCH', | Test environment variables of the system | [system/integration](../checks/system/integration/) |
| [uenv_status](../checks/system/uenv/uenv_status.py) | <none> | [system/uenv](../checks/system/uenv/) |