#!/bin/bash

echo "hello world!"

exit

rm -fr venv_reframe_cpe
python3 -m venv venv_reframe_cpe
source venv_reframe_cpe/bin/activate
pip install reframe-hpc

#reframe -c config/cscs.py ${changedtests_path} --report-junit=$REPORT -r

deactivate

