## Description

[ ] Add here a link to the Jira issue if applicable.

## Testing

### 1. Trigger CI Pipeline(s)

When your PR is ready for testing, trigger one or more CI pipelines by
commenting on this PR with `cscs-ci run`:

```shell
cscs-ci run <pipeline>;CSCS_RFM_UENV=<uenv>
```

**Examples:**

```shell
cscs-ci run alps-daint-uenv;CSCS_RFM_UENV=prgenv-gnu/26.3:v1
cscs-ci run alps-santis-uenv;CSCS_RFM_UENV=prgenv-gnu/26.3:v1
cscs-ci run alps-clariden-uenv;CSCS_RFM_UENV=prgenv-gnu/26.3:v1

cscs-ci run alps-starlex-uenv;CSCS_RFM_UENV=prgenv-gnu/26.3:v1
cscs-ci run alps-beverin-uenv;CSCS_RFM_UENV=prgenv-gnu/25.07-6.3.3:v12

cscs-ci run alps-eiger-uenv;CSCS_RFM_UENV=prgenv-gnu/26.3:v1
cscs-ci run alps-pilatus-uenv;CSCS_RFM_UENV=prgenv-gnu/26.3:v1
```

- You can test more uenvs via `CSCS_RFM_UENV=[build::|service::]prgenv-gnu/26.3[+daint]` (note the use of `+` instead of `@`)

- You can pass additional SLURM options via `CSCS_RFM_EXTRA="-J reservation=uss140-shs131-nv590-staging"`

Notes:

Other supported variables you can set in the same way:
`CSCS_RFM_CPE_CE`, `CSCS_RFM_DIR`, `CSCS_RFM_ONEUPTIME_APIKEY`, `CSCS_RFM_TARGET_DIR`, `CSCS_RFM_USER_ENV_CUDA_VISIBLE`, `CSCS_RFM_USER_ENV_IMAGE`, `CSCS_RFM_USER_ENV_ROOT`

### 2. Non uenv testing

To run the non-uenv pipeline (container/integration tests, or any test not
requiring a uenv), use the `alps-<system>` triggers instead. These run
`ci/alps.yml` with `--mode daily_production` and no `CSCS_RFM_UENV`, so
tests gated on `+uenv` are automatically skipped.

```shell
cscs-ci run alps-daint
cscs-ci run alps-santis
cscs-ci run alps-clariden
cscs-ci run alps-starlex

cscs-ci run alps-eiger
```

### 3. Local Testing (optional)

Install ReFrame: https://confluence.cscs.ch/spaces/reframe/pages/886276110/Installing+ReFrame

Example — run `cp2k` and `icon4py` checks on `beverin`:

```shell
CSCS_RFM_UENV=prgenv-gnu/25.07-6.3.3:v8 \
  reframe -C config/cscs.py \
  --keep-stage-files \
  -c checks/microbenchmarks/gpu/gpu_benchmarks/icon4py.py \
  -c checks/apps/cp2k/cp2k_uenv.py \
  --system beverin:mi300
```

---

Thank you for contributing to `cscs-reframe-tests`!

> **CSCS staff:** See https://confluence.cscs.ch/spaces/reframe → *Contributing / Pull Requests* for internal guidelines.
