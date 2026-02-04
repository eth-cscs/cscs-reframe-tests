# Copyright 2026 ETHZ/CSCS
# See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn

@rfm.simple_test
class ddBlockSizeTest(rfm.RunOnlyRegressionTest):
    """
    Reproduce the behaviour of sbatch_dd_repro.sh:
      - runs dd write tests with different block sizes
        - 1M and 5M (control runs) and 4096000 (hangs indefinitely)
    
    Original script link:
    https://github.com/eth-cscs/alps-gh200-reproducers/blob/main/stuck-node-on-io/sbatch_dd_repro.sh
    """
 
    descr = "dd write tests with different block sizes"
    valid_systems = ['*']
    valid_prog_environs = ['builtin']
    tags = {"maintenance", "production"}
    maintainers = ["VCUE", "gppezzi"]

    # bs=4096000 can potentially trigger node issues
    prob_block_size = variable(int, value=4096000)
    count = variable(int, value=1000)
    test_path = variable(str, value="$SCRATCH/ddBlockSizeTest")
    
    @run_before('run')
    def set_commands(self):
        self.executable = "/bin/bash"
        self.executable_opts = [f''' 

        mkdir -p {self.test_path}

        sleep 5
        
        for ntasks in 1 2; do
            for bs in 1M 5M {self.prob_block_size}; do
            
                echo "------------------------------------------"
                echo "Running dd with bs=$bs and ntasks=$ntasks count={self.count} path={self.test_path}/dd_largefile.$bs.$SLURM_PROCID"

                /usr/bin/dd if=/dev/zero of={self.test_path}/dd_largefile.$bs.$SLURM_PROCID bs=$bs count={self.count} status=progress

                echo "Finished."

                rm {self.test_path}/dd_largefile.*
                sleep 5
            done
        done

        echo "SUCCESS"
        '''] 
        
    @sanity_function
    def check_success(self):
        return sn.all([
            sn.assert_found(r"SUCCESS", self.stdout),
        ])
    