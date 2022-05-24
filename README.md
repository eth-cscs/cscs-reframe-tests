# ReFrame test suite of CSCS


The tests are daily checked against the tip of the `master` branch of [ReFrame](https://github.com/reframe-hpc/reframe/). 
Several tests are built on top of the `hpctestlib` library that is provided with ReFrame.

To run the test suite you need to clone ReFrame first and then this repo:

```
git clone https://github.com/reframe-hpc/reframe.git
cd reframe
git clone https://github.com/eth-cscs/cscs-reframe-tests
```

You can then run the tests on any CSCS supported machine as follows:

```
./bin/reframe -C cscs-reframe-tests/config/cscs.py -c cscs-reframe-tests/checks -R -r
```

You could also clone the tests in a separate directory (outside the ReFrame clone), but in this case you should set the `PYTHONPATH` to point to the various `hpctestlib` subdirectories of your ReFrame clone.
