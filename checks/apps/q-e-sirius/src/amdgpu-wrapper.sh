#!/bin/bash -eu

# gpu id attached to l3 cache
declare -A l3_to_gpu=(
    [0]=4
    [1]=5
    [2]=2
    [3]=3
    [4]=6
    [5]=7
    [6]=0
    [7]=1
)

# get l3 cache of current cpu mask
l3=$(hwloc-calc --physical --intersect L3 $(taskset -p $$ | awk '{print "0x"$6}'))
numanode=$(hwloc-calc --physical --intersect NUMAnode $(taskset -p $$ | awk '{print "0x"$6}'))
ROCR_VISIBLE_DEVICES=${l3_to_gpu[${l3}]}
export ROCR_VISIBLE_DEVICES

exec numactl --membind=$numanode "$@"
