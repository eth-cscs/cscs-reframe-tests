- [ ] Describe the purpose of this pull request (Add a link to the jira issue when possible)
- [ ] Share the command line used to run the test
```console
$ reframe -r ...
```

- You can manually trigger 1 (or more) CI pipelines from github by writing a comment in this Pull Request:

```shell
cscs-ci run alps-eiger-uenv;MY_UENV=prgenv-gnu/24.11:v2

cscs-ci run alps-daint-uenv;MY_UENV=prgenv-gnu/25.11:rc1
cscs-ci run alps-santis-uenv;MY_UENV=prgenv-gnu/25.11:rc1

cscs-ci run alps-starlex-uenv;MY_UENV=prgenv-gnu/25.11:rc1
cscs-ci run alps-beverin-uenv;MY_UENV=prgenv-gnu/25.07-6.3.3:v9
```

- You can also test from your terminal, for example, on beverin:
    - install: https://confluence.cscs.ch/spaces/reframe/pages/886276110/Installing+ReFrame
    - run test: for example, cp2k on beverin:

```shell
UENV=prgenv-gnu/25.07-6.3.3:v8 \
    reframe -C \
    -C ./cscs-reframe-tests.git/config/cscs.py \
    --keep-stage-files \
    -c checks/microbenchmarks/gpu/gpu_benchmarks/icon4py.py \
    -c ./cscs-reframe-tests.git/checks/apps/cp2k/cp2k_uenv.py \
    --system beverin:mi300
```

Thank you for taking the time to contribute to `cscs-reframe-tests` !
