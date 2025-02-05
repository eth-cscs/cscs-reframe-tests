#!/bin/bash -l
TOOLKIT=${1:-cuda11}
LIB_PATH=${2:-$CONDA_PREFIX/lib}

if [[ $TOOLKIT == cuda* ]] ;
then
    OFI_LIB=libnccl-net.so
else
    OFI_LIB=librccl-net.so
fi

# Activate AWS NCCL plugin
export LD_LIBRARY_PATH=$LIB_PATH:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/opt/cray/libfabric/1.15.2.0/lib64/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/opt/cscs/aws-ofi-ccl-plugin/$TOOLKIT/:$LD_LIBRARY_PATH
export LD_PRELOAD=/opt/cscs/aws-ofi-ccl-plugin/$TOOLKIT/$OFI_LIB
export CXI_FORK_SAFE="1"
export CXI_FORK_SAFE_HP="1"
export FI_CXI_DISABLE_CQ_HUGETLB="1"
export NCCL_CROSS_NIC="1"
export NCCL_DEBUG="Info"
export NCCL_NET_GDR_LEVEL="PHB"
export FI_CXI_DISABLE_HOST_REGISTER="1"
export FI_MR_CACHE_MONITOR="userfaultfd"
