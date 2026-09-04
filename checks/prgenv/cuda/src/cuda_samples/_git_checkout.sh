#!/bin/bash

in=$1
if [ -z $in ] ; then exit -1 ; fi

cd $in

# Retrieve the CUDA version from nvcc and checkout matching tag
export CUDA_VER=v$(nvcc -V | sed -n 's/^.*release \([[:digit:]]*\.[[[:digit:]]\).*$/\1/p')

# tags v12.[6-7] do not exist, checkout v12.8 instead
[[ $CUDA_VER = 'v12.6' || $CUDA_VER = 'v12.7' ]] && export CUDA_VER='v12.8'

echo CUDA_VER=$CUDA_VER
git checkout ${CUDA_VER}

cd -
