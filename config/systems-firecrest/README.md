# How to run Reframe with the firecrest scheduler

## Prerequisites

- Firecrest client set up: https://user.cscs.ch/tools/firecrest/#oidc-client-registration-management
- Requirements need to be installed before running. You can find the list [here](../utilities/requirements.txt).

## Configuration Setup

You can use the `config/cscs.py` config with the following env vars:
```bash
# Select the firecrest configuration files that support the firecrest scheduler
RFM_FIRECREST=1

# The `RFM_RESOLVE_MODULE_CONFLICTS` var is not necessary for version >=4.6. Bugfix https://github.com/reframe-hpc/reframe/pull/3093
RFM_RESOLVE_MODULE_CONFLICTS=0

# Create and set up your FirecREST client
FIRECREST_CLIENT_ID=
FIRECREST_CLIENT_SECRET=
AUTH_TOKEN_URL=
# The URL of a FirecREST v2 deployment
FIRECREST_URL=

# You can optionally set the version of the FirecREST v2 API that you are
# using (by default the client assumes >=2.5.4)
FIRECREST_API_VERSION="2.5.4"

# This variable defines the name of the system from the point of view of FirecREST
FIRECREST_SYSTEM=daint

# Select the base directory on the system where the tests will be running from
FIRECREST_BASEDIR=

# In case the tests need compilation you have to pass this in the command in order to build them in the remote partitions
reframe -C /path/to/cscs-reframe-tests/config/cscs.py ... -Sbuild_locally=0
```

The processor autodetection can be really slow, so we recommend to skip it for now.
