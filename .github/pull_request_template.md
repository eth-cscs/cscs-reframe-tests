- [ ] Describe the purpose of this pull request (Add a link to the jira issue when possible)
- [ ] When ready, manually trigger 1 (or more) CI pipelines by writing a cscs-ci comment inside this Pull Request.
For instance:

```shell
cscs-ci run alps-daint-uenv;CSCS_RFM_UENV=prgenv-gnu/26.3:v1
cscs-ci run alps-santis-uenv;CSCS_RFM_UENV=prgenv-gnu/26.3:v1
cscs-ci run alps-clariden-uenv;CSCS_RFM_UENV=prgenv-gnu/26.3:v1

cscs-ci run alps-starlex-uenv;CSCS_RFM_UENV=prgenv-gnu/25.11:v1
cscs-ci run alps-beverin-uenv;CSCS_RFM_UENV=prgenv-gnu/25.07-6.3.3:v12

cscs-ci run alps-eiger-uenv;CSCS_RFM_UENV=[build::|service::]prgenv-gnu/25.11:v1
```

- You can also pass SLURM flags:
    - cscs-ci run alps-starlex-uenv;CSCS_RFM_UENV=prgenv-gnu/25.11:v1;CSCS_RFM_EXTRA="-J reservation=uss140-shs131-nv590-staging"
    - note:
        - the group of the reframe user currently is djenkssl, not csstaff, check the allowed groups in the reservation,
        - the default SLURM_TIMELIMIT is set to 2h, check the allowed MaxTime in the partition.

- You can also test from your terminal:
    - install: https://confluence.cscs.ch/spaces/reframe/pages/886276110/Installing+ReFrame
    - run test: for example, cp2k on beverin:

```shell
CSCS_RFM_UENV=prgenv-gnu/25.07-6.3.3:v8 \
    reframe -C \
    -C ./cscs-reframe-tests.git/config/cscs.py \
    --keep-stage-files \
    -c checks/microbenchmarks/gpu/gpu_benchmarks/icon4py.py \
    -c ./cscs-reframe-tests.git/checks/apps/cp2k/cp2k_uenv.py \
    --system beverin:mi300
```

Other variables: CSCS_RFM_CPE_CE, CSCS_RFM_DIR,
CSCS_RFM_ONEUPTIME_APIKEY, CSCS_RFM_TARGET_DIR,
CSCS_RFM_USER_ENV_CUDA_VISIBLE, CSCS_RFM_USER_ENV_IMAGE,
CSCS_RFM_USER_ENV_ROOT

Thank you for taking the time to contribute to `cscs-reframe-tests` !
- CSCS staff: More info in https://confluence.cscs.ch/spaces/reframe --> Contributing+Pull+Requests
