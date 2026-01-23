import reframe as rfm
import reframe.utility.sanity as sn

@rfm.simple_test
class ddBlockSizeTest(rfm.RunOnlyRegressionTest):
    """
    Reproduce the behaviour of sbatch_dd_repro.sh:
      - run a series of dd write tests with different block sizes 
    
    Original script link:
    https://github.com/eth-cscs/alps-gh200-reproducers/blob/main/stuck-node-on-io/sbatch_dd_repro.sh
    """
 
    descr = "dd write tests with different block sizes"
    valid_systems = ['+remote']              
    valid_prog_environs = ['builtin']
    
    @run_before('run')
    def set_commands(self):
        self.executable = "bash"
        self.executable_opts = ["-c", f'''
        OUT=./
        mkdir -p $OUT

        sleep 5

        for ntasks in 1 2; do
            for bs in 1M 2M 3M 4M 5M 4096000; do
            
                echo "------------------------------------------"
                echo "Running dd with bs=$bs and ntasks=$ntasks"
            
                srun -ul -n$ntasks \
                bash -c "dd if=/dev/zero of=$OUT/dd_largefile.\$SLURM_PROCID bs=$bs count=1000 status=progress"
            
                echo "Finished."
            
                rm $OUT/dd_largefile.*
                sleep 5
            done
        done

        echo
        echo "SUCCESS"
        '''] 
        
    @sanity_function
    def check_success(self):
        return sn.all([
            sn.assert_found(r"SUCCESS", self.stdout),
        ])