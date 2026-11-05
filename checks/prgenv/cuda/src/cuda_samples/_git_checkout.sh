#!/bin/bash

# will checkout the tag matching the version of cuda in the uenv
# tested with 12.9, 13.1 and 13.4, will revisit when getting new uenvs

set -euo pipefail

in=${1:-}
if [ -z "$in" ] ; then exit 1 ; else cd "$in" ; fi

# Retrieve the CUDA version from nvcc and checkout matching tag
CUDA_VER=v$(nvcc -V | sed -n 's/^.*release \([[:digit:]]*\.[[:digit:]]*\).*$/\1/p')
# for reference, tags v12.[6-7] do not exist, checkout v12.8 instead
[[ "$CUDA_VER" = 'v12.6' || "$CUDA_VER" = 'v12.7' ]] && export CUDA_VER='v12.8'

echo CUDA_VER=$CUDA_VER
# fails (and stops the build) if there is no tag for this CUDA version
git checkout "${CUDA_VER}"
