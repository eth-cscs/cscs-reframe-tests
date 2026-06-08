[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/eth-cscs/cscs-reframe-tests)
![GitHub contributors](https://img.shields.io/github/contributors-anon/eth-cscs/cscs-reframe-tests)<br/>

# ReFrame test suite of CSCS

The tests are checked daily on CSCS systems using a recent version of
[ReFrame](https://github.com/reframe-hpc/reframe/).

## Running on a CSCS system

To run the test suite you need first to install ReFrame and then the repository
with the tests:

### Install ReFrame

- Follow the instructions from https://github.com/reframe-hpc/reframe#installation

### Clone the tests

```
git clone https://github.com/eth-cscs/cscs-reframe-tests
```

You can then list all the tests on any CSCS supported machine as follows:

```
reframe -C cscs-reframe-tests/config/cscs.py -c cscs-reframe-tests/checks/ -R -l
```

## Local development setup

- Follow the instructions from https://reframe-hpc.readthedocs.io/en/latest/tutorial.html#reframe-tutorial

