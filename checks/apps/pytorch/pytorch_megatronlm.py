# Copyright 2025 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from container_engine import ContainerEngineMixin  # noqa: E402


class PyTorchMegatronLM(rfm.RunOnlyRegressionTest):
    num_tasks_per_node = 4
    num_nodes = variable(int, value=16)
    time_limit = '2h'

    # The Megatron commit id
    commit_id = variable(str, value='de14c22')

    # The LLM model to run
    model = variable(str, value='llama3-8b')

    # The number of checkpoint steps
    checkpoint_steps = variable(int, value=500)

    # The number of training steps
    training_steps = variable(int, value=50)

    # Use WANDB logging 
    wandb_logging = variable(bool, value=False)

    # The dataset paths to use.
    # Multiple paths can be passed using ',' as path separator.
    # Mock data is going to be used if the value is `None`.
    datasets = variable(str, type(None), value=None)

    configurations = {
        'llama3-70b': {
            'micro_batch_size': 1,
            'global_batch_size': 1024,
            'sequence_length': 8192,
            'num_layers': 80,
            'hidden_size': 8192,
            'ffn_hidden_size': 28672,
            'num_attention_heads': 64,
            'tensor_model_parallel_size': None,
            'pipeline_model_parallel_size': 8,
            'num_layers_per_virtual_pipeline_stage': 5,
            'context_parallel_size': 1,
            'lr': '0.00015',
            'min_lr': '0.000015',
            'manual_gc_interval': '50',
            'wgrad_deferral_limit': 22,
            'sequence_parallel': True,
            'defer_embedding_wgrad_compute': True,
            'overlap_p2p_communication_warmup_flush': True
        },
        'llama3-8b': {
            'micro_batch_size': 1,
            'global_batch_size': 128,
            'sequence_length': 8192,
            'num_layers': 32,
            'hidden_size': 4096,
            'ffn_hidden_size': 14336,
            'num_attention_heads': 32,
            'tensor_model_parallel_size': 1,
            'pipeline_model_parallel_size': 1,
            'lr': '0.00022',
            'min_lr': '0.000022',
            'manual_gc_interval': '500',
            'sequence_parallel': False,
            'defer_embedding_wgrad_compute': False,
            'overlap_p2p_communication_warmup_flush': False 
        }
    }

    sourcesdir = None 
    executable = 'bash'

    tags = {'production', 'ml'}

    @run_after('setup')
    def setup_test(self):
        curr_part = self.current_partition
        self.num_gpus_per_node = curr_part.select_devices('gpu')[0].num_devices
        self.num_tasks = self.num_nodes * self.num_gpus_per_node
        #self.num_cpus_per_task = (curr_part.processor.num_cpus // 
        #                          self.num_tasks_per_node)

    @run_after('setup')
    def set_executable_opts(self):
        model_config = self.configurations[self.model]
        self.env_vars = {
            'TORCH_NCCL_AVOID_RECORD_STREAMS': 1,
            'TORCH_NCCL_ASYNC_ERROR_HANDLING': 1,
            'NCCL_DEBUG': 'Info',
            'CUDA_DEVICE_MAX_CONNECTIONS': 1,
            'MASTER_ADDR':
                '$(scontrol show hostnames $SLURM_JOB_NODELIST | head -n 1)',
            'MASTER_PORT': '6000',
            'WORLD_SIZE': '$SLURM_NPROCS',
            'MEGATRON_LM_DIR': '$PWD/Megatron-LM',
            'PYTHONPATH': '$MEGATRON_LM_DIR:$PYTHONPATH',
            'PROJECT_NAME': 'Megatron-Clariden',
            'EXP_NAME': f'{self.model}-$SLURM_NNODES-nodes',
            'PROJECT_DIR': '$MEGATRON_LM_DIR/logs/Meg-Runs/$PROJECT_NAME',
            'EXP_DIR': '$PROJECT_DIR/$EXP_NAME',
            'CKPT_DIR': '$EXP_DIR/checkpoints',
            'TRIGGER_DIR': '$EXP_DIR/triggers',
            'DEBUG_DIR': '$EXP_DIR/debug/$SLURM_JOB_ID',
            'COMPUTE_ENVIRONMENT_DIR': '$DEBUG_DIR/compute_environment.txt',
            'GPU_MEM_LOGGING': '$DEBUG_DIR/memory_logging.txt',
            'LOGGING_DIR': '$EXP_DIR/logging',
            'TENSORBOARD_DIR': '$LOGGING_DIR/tensorboard',
            'BACKUP_CODEBASE_DIR': '$EXP_DIR/Megatron-LM',
            'DATASET_CACHE_DIR': '$PWD/datasets/cache',
        }
        self.prerun_cmds = [
            f'git clone https://github.com/swiss-ai/Megatron-LM.git',
            f'cd $MEGATRON_LM_DIR',
            f'git checkout {self.commit_id}',
            f'echo "START TIME: $(date)"',
            f'ulimit -c 0',
            f'mkdir -p $CKPT_DIR',
            f'mkdir -p $PROJECT_DIR',
            f'mkdir -p $TRIGGER_DIR',
            f'mkdir -p $DEBUG_DIR',
            f'mkdir -p $LOGGING_DIR',
        ]

        if self.datasets is not None:
            self.prerun_cmds += [
                f'export DATAPATH_CONFIGURED=$(python3 $MEGATRON_LM_DIR'
                f'/scripts/tools/create_data_config.py -p {self.datasets})'
            ]

        self.postrun_cmds = ['echo "END TIME: $(date)"']
        cmd_prefix = 'numactl --membind=0-3'

        transformer_engine_args = [
	    '--transformer-impl transformer_engine',
	    '--use-precision-aware-optimizer',
	    '--main-grads-dtype bf16'
        ]

        network_size_args = [
	    f'--num-layers {model_config["num_layers"]}',
	    f'--hidden-size {model_config["hidden_size"]}',
	    f'--ffn-hidden-size {model_config["ffn_hidden_size"]}',
	    f'--num-attention-heads {model_config["num_attention_heads"]}',
	    f'--group-query-attention',
	    f'--num-query-groups 8',
	    f'--max-position-embeddings {model_config["sequence_length"]}',
	    f'--position-embedding-type rope',
	    f'--rotary-base 500000',
	    f'--use-rope-scaling',
	    f'--rope-scaling-factor 8',
	    f'--make-vocab-size-divisible-by 128',
	    f'--normalization RMSNorm',
	    f'--swiglu',
	    f'--untie-embeddings-and-output-weights',
        ]

        logging_args = [
	    '--log-throughput',
	    '--log-progress',
	    '--tensorboard-dir $TENSORBOARD_DIR',
	    '--no-log-loss-scale-to-tensorboard',
	    '--log-memory-to-tensorboard'
        ]

        if self.wandb_logging:
            if 'WANDB_API_KEY' in os.environ:
                logging_args += [
                    '--wandb-save-dir $LOGGING_DIR',
                    '--wandb-project $PROJECT_NAME',
                    '--wandb-exp-name $EXP_NAME-$SLURM_JOB_ID'
                ]
            else:
                self.skip_if(
                    True, 'WANDB logging requested but WANDB_API_KEY not set'
                )
        else:
            self.env_vars['WANDB_MODE'] = 'disabled'

        regularization_args = [
	    '--attention-dropout 0.0',
	    '--hidden-dropout 0.0',
	    '--weight-decay 0.1',
	    '--clip-grad 1.0',
	    '--adam-beta1 0.9',
	    '--adam-beta2 0.95',
        ]

        training_args = [
	    f'--micro-batch-size {model_config["micro_batch_size"]}',
	    f'--global-batch-size {model_config["global_batch_size"]}',
	    f'--no-check-for-nan-in-loss-and-grad',
	    f'--train-iters {self.training_steps}',
	    f'--log-interval 1',
	    f'--eval-iters 0',
	    f'--cross-entropy-loss-fusion',
	    f'--disable-bias-linear',
	    f'--optimizer adam',
	    f'--dataloader-type single',
	    f'--manual-gc',
	    f'--manual-gc-interval {model_config["manual_gc_interval"]}',
	    f'--exit-signal-handler',
	    f'--trigger-path $TRIGGER_DIR',
        ]

        initialization_args = [ 
	    '--seed 28',
	    '--init-method-std 0.008944'
        ]

        learning_rate_args = [ 
	    f'--lr {model_config["lr"]}',
	    f'--min-lr {model_config["min_lr"]}',
	    f'--lr-decay-style cosine',
	    f'--lr-warmup-iters 1',
        ] 

        checkpoint_args = [ 
	    f'--save $CKPT_DIR',
	    f'--save-interval {self.checkpoint_steps}',
	    f'--ckpt-format torch_dist',
	    f'--load $CKPT_DIR',
	    f'--async-save'
        ]

        mixed_precision_args = [
	    '--bf16'
        ]

        distributed_args = [ 
            f'--tensor-model-parallel-size ' 
            f'{model_config["tensor_model_parallel_size"] or self.num_gpus_per_node}',
            f'--pipeline-model-parallel-size '
            f'{model_config["pipeline_model_parallel_size"]}',
            f'--use-distributed-optimizer',
            f'--overlap-grad-reduce',
            f'--overlap-param-gather',
        ]

        extra_distributed_args = [
            'num_layers_per_virtual_pipeline_stage',
            'context_parallel_size',
            'wgrad_deferral_limit',
        ] 

        for ar in extra_distributed_args:
            if ar in model_config:
                distributed_args += [
                    f'--{ar.replace("_", "-")} {model_config[ar]}'
                ]
 
        extra_distributed_args_boolean = [
            'sequence_parallel',
            'defer_embedding_wgrad_compute',
            'overlap_p2p_communication_warmup_flush'
        ]

        for ar in extra_distributed_args_boolean:
            if model_config[ar]:
                distributed_args += [f'--{ar.replace("_", "-")}']


        tokenizer_args = [
	    '--tokenizer-type HuggingFaceTokenizer',
	    '--tokenizer-model alehc/swissai-tokenizer'
        ]

        data_args = [
	    f'--split 100,0,0',
	    f'--seq-length {model_config["sequence_length"]}',
	    f'--reset-position-ids',
	    f'--reset-attention-mask',
	    f'--eod-mask-loss',
	    f'--num-workers 1',
	    f'--num-dataset-builder-threads 1',

        ]

        if self.datasets is None:
            data_args += ['--mock-data']
        else:
            data_args += [
                '--data-path $DATAPATH_CONFIGURED',
                '--data-cache-path $DATASET_CACHE_DIR'
            ]

        all_args = [ 
            *transformer_engine_args,
            *network_size_args,
            *logging_args,
            *regularization_args,
            *training_args,
            *initialization_args,
            *learning_rate_args,
            *checkpoint_args,
            *mixed_precision_args,
            *distributed_args,
            *tokenizer_args,
            *data_args
        ]

        training_cmd = ( 
            f'python $MEGATRON_LM_DIR/pretrain_gpt.py {" ".join(all_args)}'
        )
     
        self.executable_opts = [
            rf"-c", 
            # Open with single quote
            rf"'RANK=$SLURM_PROCID LOCAL_RANK=$SLURM_LOCALID "
            rf"PYTHONPATH=$MEGATRON_LM_DIR:$PYTHONPATH "
            rf"{cmd_prefix} "

            # Close with single quote
            rf"{training_cmd}'"
        ]

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r'Training finished after \d+ iterations',
                               self.stdout)

    @performance_function('tokens/sec/gpu')
    def tokens_per_sec_per_gpu(self):
        return sn.avg(
            sn.extractall(r'tokens/sec/gpu:\s*(?P<tokens>\S+)',
                          self.stdout, tag='tokens', conv=float
            )
        )

    @performance_function('TFLOP/s/GPU')
    def throughput_per_gpu(self):
        return sn.avg(sn.extractall(
            r'throughput per GPU \(TFLOP/s/GPU\):\s*(?P<throughput>\S+)',
            self.stdout, tag='throughput', conv=float
        ))


@rfm.simple_test
class PyTorchMegatronLM_CE(PyTorchMegatronLM, ContainerEngineMixin):
    valid_systems = ['+nvgpu +ce']
    valid_prog_environs = ['builtin']
    image = '/iopsstor/scratch/cscs/manitart/swissai_container_image/torch_25.03.sqsh'

    @run_after('init')
    def set_container_config(self):
        self.container_image = self.image
        self.container_env_table = {
            'annotations.com.hooks': {
                'aws_ofi_nccl.enabled': 'true',
                'aws_ofi_nccl.variant': 'cuda12',
            },
       }

    @run_after('setup')
    def set_container_mounts(self):
        # Ensure that the various dirs related to PROJECT_DIR are accessible
        # from within the container
        self.container_mounts = [f'{self.stagedir}:{self.stagedir}']
        if self.datasets is not None:
            for dataset in self.datasets.split(','):
                self.container_mounts += [f'{dataset}:{dataset}']


@rfm.simple_test
class PyTorchMegatronLM_UENV(PyTorchMegatronLM):
    valid_systems = ['+nvgpu +uenv']
    valid_prog_environs = ['+pytorch']

    @run_after('setup')
    def patch_numpy(self):
        # np.product -> np.prod in latest NumPy versions
        self.prerun_cmds += [
            r"grep -r -l 'np\.product' ${MEGATRON_LM_DIR} | "
            r"xargs sed -i 's/np.product/np.prod/g'"
        ]

    @run_after('setup')
    def set_env_vars(self):
        self.env_vars.update({
            'TRITON_CACHE_DIR': '$MEGATRON_LM_DIR/.triton_cache',
            'NCCL_CROSS_NIC': 1,
            'NCCL_NET_GDR_LEVEL': 'PHB',
            'NCCL_NET': '"AWS Libfabric"',
            'FI_CXI_DISABLE_HOST_REGISTER': 1,
            'FI_MR_CACHE_MONITOR': 'userfaultfd',
            'FI_CXI_DEFAULT_CQ_SIZE': 131072,
            'FI_CXI_DEFAULT_TX_SIZE': 32768,
            'FI_CXI_RX_MATCH_MODE': 'software',
        })
