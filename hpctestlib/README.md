# Vendored `hpctestlib`

This directory contains a subset of ReFrame's `hpctestlib`, copied verbatim
from the ReFrame repository at tag `v4.10.3`
(https://github.com/reframe-hpc/reframe/tree/v4.10.3/hpctestlib).
Since ReFrame 4.10.0 the packages published on PyPI no longer include
`hpctestlib`.
They will not be supported in the future releases.

## Contents

- `microbenchmarks/gpu/` (GPU burn, DGEMM, kernel latency, memory bandwidth,
  pointer chase, shared memory, and the common `Xdevice` headers)
- `python/numpy/`
- `interactive/jupyter/ipcmagic/`
- `ml/pytorch/horovod.py`, `ml/tensorflow/horovod.py`
