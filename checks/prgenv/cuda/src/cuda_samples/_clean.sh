#!/bin/bash

dirn=$1
# example: 'cuda-samples/Samples/1_Utilities/deviceQuery'
if [ -z $dirn ] ; then exit -1 ; else echo "cleaning $dirn" ; fi

rm -fr cuda-samples/bin/win64

# --- level1
_wdir=$(echo $dirn |cut -d/ -f1,2) # cuda-samples/Samples/
_keep=$(echo $dirn |cut -d/ -f3)  # 1_Utilities
cd $_wdir
_delete=$(ls -I CMakeLists.txt -I $_keep)
_cmd="rm -fr $_delete"
echo $_cmd
$_cmd
cd -

# --- level2
_wdir=$(echo $dirn |cut -d/ -f1,2,3) # cuda-samples/Samples/1_Utilities/
_keep=$(echo $dirn |cut -d/ -f4)     # deviceQuery
cd $_wdir
_delete=$(ls -I CMakeLists.txt -I $_keep)
_cmd="rm -fr $_delete"
echo $_cmd
$_cmd
cd -

