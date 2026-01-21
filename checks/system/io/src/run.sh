#!/bin/bash

function fail()
{
    echo $1
    exit 1
}

FASTDISK=/iopsstor/scratch/cscs/perettig/
LARGEFILE=${FASTDISK}/gpu-stuckmem.tmp

/usr/bin/parallel_allocate_free_gpu_mem 95 || fail "First allocation failed. Is this a clean node with file cached already flushed?"

echo "======================================================================="
echo
echo "  Memory state before IO"
echo
echo "======================================================================="
echo
nvidia-smi
numastat -m -z | grep -v "not in hash table"

echo
echo "======================================================================="
echo
echo "  Performing heavy IO operation"
echo
echo "======================================================================="
echo
numactl --membind=0 fio --name=cachetest --rw=read --size=100G --filename=${LARGEFILE} --bs=1M --ioengine=sync --direct=0

echo
echo "======================================================================="
echo
echo "  Memory state after IO"
echo
echo "======================================================================="
echo
nvidia-smi
numastat -m -z | grep -v "not in hash table"

echo
echo
/usr/bin/parallel_allocate_free_gpu_mem 95 || fail "Last allocation failed. Stuck memory bug still present. Check FilePages in numastat output above."

