# How to run ReFrame with the firecrest scheduler

## Prerequisites

- A FirecREST v2 client: https://eth-cscs.github.io/firecrest-v2/
- Requirements need to be installed before running. You can find the list [here](../utilities/requirements.txt).

## Configuration Setup

You can use the `config/cscs.py` config with the following env vars:
```bash
# Select the firecrest configuration files that support the firecrest scheduler
CSCS_RFM_FIRECREST=1

# Create and set up your FirecREST client
FIRECREST_CLIENT_ID=
FIRECREST_CLIENT_SECRET=
AUTH_TOKEN_URL=
# The URL of a FirecREST v2 deployment
FIRECREST_URL=

# You can optionally set the version of the FirecREST v2 API that you are
# using (by default the client assumes >=2.5.4)
FIRECREST_API_VERSION="2.5.4"

# This variable defines the name of the system from the point of view of
# FirecREST; it is also used to select the ReFrame system configuration
FIRECREST_SYSTEM=daint

# Select the base directory on the system where the tests will be running from
FIRECREST_BASEDIR=

# Optionally select the Slurm account to submit the jobs with; when unset,
# the default account of the user is used
CSCS_RFM_FIRECREST_ACCOUNT=

# In case the tests need compilation you have to pass this in the command in
# order to build them in the remote partitions
reframe -C /path/to/cscs-reframe-tests/config/cscs.py ... -Sbuild_locally=0
```

The processor autodetection can be really slow through FirecREST, so it is disabled in these configurations (`remote_detect: False`).
