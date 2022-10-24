#!/bin/bash
# export MPICH_VERSION_DISPLAY=1
export MPICH_OFI_NIC_VERBOSE=1
case $SLURM_LOCALID in
    0)
    export LOCAL_RANK=0
    export CUDA_VISIBLE_DEVICES=0
    export MPICH_OFI_NIC_POLICY=USER
    export MPICH_OFI_NIC_MAPPING="0:1,3; 1:0,2"
    numactl --physcpubind=48-63 --membind=3 $*
    # -s
    ;;
    1)
    export LOCAL_RANK=1
    export CUDA_VISIBLE_DEVICES=1
    export MPICH_OFI_NIC_POLICY=USER
    export MPICH_OFI_NIC_MAPPING="0:1,3; 1:0,2"
    numactl --physcpubind=32-47 --membind=2 $*
    ;;
    2)
    export LOCAL_RANK=2
    export CUDA_VISIBLE_DEVICES=2
    export MPICH_OFI_NIC_POLICY=USER
    export MPICH_OFI_NIC_MAPPING="0:1,3; 1:0,2"
    numactl --physcpubind=16-31 --membind=1 $*
    ;;
    3)
    export LOCAL_RANK=1
    export CUDA_VISIBLE_DEVICES=3
    export MPICH_OFI_NIC_POLICY=USER
    export MPICH_OFI_NIC_MAPPING="0:1,3; 1:0,2"
    numactl --physcpubind=0-15 --membind=0 $*
    ;;
    *)
    echo Warning: unknown SLURM_LOCALID=$SLURM_LOCALID
    ;;
esac
