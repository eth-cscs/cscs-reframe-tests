# ReFrame test suite of CSCS


The tests are daily checked against the tip of the `master` branch of [ReFrame](https://github.com/reframe-hpc/reframe/). 
Several tests are built on top of the `hpctestlib` library that is provided with ReFrame.

To run the test suite you need first to clone and bootstrap ReFrame and then this repo:


## Install ReFrame
```
git clone https://github.com/reframe-hpc/reframe.git
pushd reframe
./bootstrap.sh
export PATH=$(pwd)/bin:$PATH
popd
```

## Clone the tests

```
git clone https://github.com/eth-cscs/cscs-reframe-tests
cd cscs-reframe-tests
```


## Set-up Python Virtual environement

Install python3.11 on your machine.

Create a virtual environment:
```console
python3.11 -m venv --system-site-packages .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run and Debug
```console
cd cscs-reframe-tests
source .venv/bin/activate

reframe -V

reframe \
-C config/cscs.py \
-c checks/microbenchmarks/gpu/node_burn/baremetal-node-burn.py \
-l \
--skip-prgenv-check --skip-system-check

```
