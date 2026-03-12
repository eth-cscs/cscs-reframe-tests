#!/bin/bash

driver_ver=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | cut -d. -f1)
echo "driver_version=$driver_ver"

for param in uvm_perf_access_counter_migration_enable uvm_perf_access_counter_mimc_migration_enable; do
    path="/sys/module/nvidia_uvm/parameters/$param"
    if [ -f "$path" ]; then
        echo "$param=$(cat $path)"
    fi
done
