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

You can then list all the tests on any CSCS supported machine as follows:

```
reframe -C config/cscs.py -c checks/ -R -l
```


## Set-up Python Virtual environement

Install python3.12 on your machine.

Create a virtual environment:
```console
python3.12 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt


## Debug 