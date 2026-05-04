## Eligible ReFrame Tests on daint

- Filters:
  - system: `daint`
  - tags: `vs-node-validator`
  - checks: `3`
- Generated: `2026-05-05 15:16:52 +0200`

| Test name | Description | Category |
|----------|-------------|----------|
| [uenv_status](../checks/system/uenv/uenv_status.py) | — | [system/uenv](../checks/system/uenv/) |
| [uenv_status](../checks/system/uenv/uenv_status.py) | — | [system/uenv](../checks/system/uenv/) |
| [DcgmRpmCheck](../checks/system/gssr/dcgm_hook.py) | Check DCGM executable and libraries are installed | [system/gssr](../checks/system/gssr/) |
| [GssrCeHookCheck](../checks/system/gssr/dcgm_hook.py)<br>• %pytorch_image_tag=25.01-py3_nvrtc-12.9 | Check DCGM CE hook is working with gssr | [system/gssr](../checks/system/gssr/) |