import os
import sys

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class slurm_jg(rfm.RunOnlyRegressionTest):
    valid_prog_environs = ['*']
    valid_systems = ['*']
    executable = 'echo'
    time_limit = '1m'
    num_tasks = 1
    # num_tasks_per_node = 1

#test     @run_after('setup')
#test     def skip_python_version(self):
#test         # hh = os.getenv('HOME') ;print(hh)
#test         print(sys.version_info)
#test         # procinfo = self.current_partition.processor
#test         # self.skip_if(self.num_threads > procinfo.num_cores, 'not enough cores')
#test         self.skip_if(sys.version_info.minor >= 14, f'incompatible python version ({sys.version_info.minor})')

    @run_before('run')
    def set_runtime_args(self):
        # self.prerun_cmds = ["python --version |awk '{print $2}'"]
        self.executable_opts = ['A']
#            f"--nodes={config['nodes']}",                                       
#            "--ntasks-per-core=1",                                              
#            "--partition=debug",                                                
#            # "--reservation=daint",  # TODO: Remove reservation                
#        ]                                                                       
        # self.num_nodes = 1
        # self.num_tasks_per_core = 1
        # self.num_tasks_per_node = 1
        # self.num_tasks = 1
        # self.num_cpus_per_task = 1
        # self.skip_if_no_procinfo()
        #print(self.current_partition.devices[0].num_devices)

#del     @sn.deferrable
#del     def extract_python_version(self):
#del         py_version = sn.extractall(
#del         regex = r'^'
#del         # We get one column per GPU and one for the timestamp
#del         regex += ''.join(r'\s*(\d+.\d+)' for i in range(self.num_gpus + 1))
#del         regex += r'\s*\S+$'
#del         gflops = func(
#del             func(
#del                 sn.extractall(regex, self.stdout, i+1, float)
#del             ) for i in range(self.num_gpus)
#del         )
#del         return gflops

    @sanity_function
    def set_sanity(self):
        return sn.all([
            sn.assert_found(r'A', self.stdout),
        ])

