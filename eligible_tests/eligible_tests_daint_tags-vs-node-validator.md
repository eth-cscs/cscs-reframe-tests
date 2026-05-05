## Eligible ReFrame Tests on daint

- Filters:
  - system: `daint`
  - tags: `vs-node-validator`
  - checks: `3`
- Generated: `2026-05-05 16:55:30 +0200`

| Test name | Description | Category |
|----------|-------------|----------|
| ../checks/system/uenv/uenv_status.py | <none> | ../checks/system/uenv/ |
| ../checks/system/gssr/dcgm_hook.py | Check DCGM executable and libraries are installed | ../checks/system/gssr/ |
| ../checks/system/gssr/dcgm_hook.py<br>• %pytorch_image_tag=25.01-py3_nvrtc-12.9 | Check DCGM CE hook is working with gssr | ../checks/system/gssr/ |