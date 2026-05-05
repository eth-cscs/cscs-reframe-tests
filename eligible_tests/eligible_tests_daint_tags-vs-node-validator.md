## Eligible ReFrame Tests on daint

- Filters:
  - system: `daint`
  - tags: `vs-node-validator`
  - checks: `3`
- Generated: `2026-05-05 17:06:59 +0200`

| Test name | Description | Category |
|----------|-------------|----------|
| uenv_status<br>file: [../checks/system/uenv/uenv_status.py](../checks/system/uenv/uenv_status.py) | <none> | [system/uenv](../checks/system/uenv/) |
| DcgmRpmCheck<br>file: [../checks/system/gssr/dcgm_hook.py](../checks/system/gssr/dcgm_hook.py) | Check DCGM executable and libraries are installed | [system/gssr](../checks/system/gssr/) |
| GssrCeHookCheck<br>• %pytorch_image_tag=25.01-py3_nvrtc-12.9<br>file: [../checks/system/gssr/dcgm_hook.py](../checks/system/gssr/dcgm_hook.py) | Check DCGM CE hook is working with gssr | [system/gssr](../checks/system/gssr/) |