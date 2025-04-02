# Copyright 2025 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import re
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from container_engine import ContainerEngineMixin  # noqa: E402


@rfm.simple_test
class PyTorchMegatronLM(rfm.RunOnlyRegressionTest, ContainerEngineMixin):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['builtin']
    num_nodes = variable(int, value=32)
    num_tasks_per_node = 4

    micro_batch_size = variable(int, value=1)
    global_batch_size = variable(int, value=1024)
    sequence_length = variable(int, value=8192) 
    checkpoint_steps = variable(int, value=250)
    
    sourcesdir = None 
    curated_images = ['nvcr.io#nvidia/pytorch:24.12-py3']

    image = parameter(curated_images)

    executable = 'bash'

    env_vars = {
        'NCCL_DEBUG': 'Info',
        'TORCH_NCCL_AVOID_RECORD_STREAMS': 1,
        'TORCH_NCCL_ASYNC_ERROR_HANDLING': 1,
        'CUDA_DEVICE_MAX_CONNECTIONS': 1,
        'MASTER_ADDR':
            '$(scontrol show hostnames $SLURM_JOB_NODELIST | head -n 1)',
        'MASTER_PORT': '6000', 
        'WORLD_SIZE': '$SLURM_NPROCS',
        'MEGATRON_LM_DIR': '$PWD/Megatron-LM',
        'PYTHONPATH': '$MEGATRON_LM_DIR:$PYTHONPATH',
        'PROJECT_NAME': 'Megatron-Clariden',
        'EXP_NAME': 'llama3-70b-$SLURM_NNODES-nodes',
        'PROJECT_DIR': '$MEGATRON_LM_DIR/logs/Meg-Runs/$PROJECT_NAME',
        'EXP_DIR': '$PROJECT_DIR/$EXP_NAME',
        'CKPT_DIR': '$EXP_DIR/checkpoints',
        'TRIGGER_DIR': '$EXP_DIR/triggers',
        'DEBUG_DIR': '$EXP_DIR/debug/$SLURM_JOB_ID',
        'COMPUTE_ENVIRONMENT_DIR': '$DEBUG_DIR/compute_environment.txt',
        'GPU_MEM_LOGGING': '$DEBUG_DIR/memory_logging.txt',
        'LOGGING_DIR': '$EXP_DIR/logging',
        'TENSORBOARD_DIR': '$LOGGING_DIR/tensorboard',
        'BACKUP_CODEBASE_DIR': '$EXP_DIR/Megatron-LM'
    }

    tags = {'production', 'ml'}

    @run_after('init')
    def set_image(self):
        self.container_image = self.image
        self.environment_in_launcher = False
        self.container_env_table = {
            'annotations.com.hooks': {
                    'aws_ofi_nccl.enabled': 'true',
                    'aws_ofi_nccl.variant': 'cuda12',
            },
       }

    @run_after('setup')
    def setup_test(self):
        curr_part = self.current_partition
        self.num_gpus_per_node = curr_part.select_devices('gpu')[0].num_devices
        self.num_tasks = self.num_nodes * self.num_gpus_per_node
        self.num_cpus_per_task = (curr_part.processor.num_cpus // 
                                  self.num_tasks_per_node)

    @run_after('setup')
    def set_executable_opts(self):
        self.prerun_cmds = [
            'git clone https://github.com/swiss-ai/Megatron-LM.git',
            'env',
            'cd $MEGATRON_LM_DIR',
            'echo "START TIME: $(date)"',
            'ulimit -c 0',
            'mkdir -p $CKPT_DIR',
            'mkdir -p $PROJECT_DIR',
            'mkdir -p $TRIGGER_DIR',
            'mkdir -p $DEBUG_DIR',
            'mkdir -p $LOGGING_DIR',
        ]

        self.postrun_cmds = ['echo "END TIME: $(date)"']

        cmd_prefix = 'numactl --membind=0-3'

        transformer_engine_args = [
	    '--transformer-impl transformer_engine',
	    '--use-precision-aware-optimizer'
	    '--main-grads-dtype bf16'
        ]

        network_size_args = [
	    f'--num-layers 80',
	    f'--hidden-size 8192',
	    f'--ffn-hidden-size 28672',
	    f'--num-attention-heads 64',
	    f'--group-query-attention',
	    f'--num-query-groups 8',
	    f'--max-position-embeddings {self.sequence_length}',
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

        regularization_args = [
	    '--attention-dropout 0.0',
	    '--hidden-dropout 0.0',
	    '--weight-decay 0.1',
	    '--clip-grad 1.0',
	    '--adam-beta1 0.9',
	    '--adam-beta2 0.95',
        ]

        training_args = [
	    f'--micro-batch-size {self.micro_batch_size}', 
	    f'--global-batch-size {self.global_batch_size}',
	    f'--no-check-for-nan-in-loss-and-grad',
	    f'--train-iters $TRAINING_STEPS',
	    f'--log-interval 1',
	    f'--eval-iters 0',
	    f'--cross-entropy-loss-fusion',
	    f'--disable-bias-linear',
	    f'--optimizer adam',
	    f'--dataloader-type single',
	    f'--manual-gc',
	    f'--manual-gc-interval 50',
	    f'--exit-signal-handler',
	    f'--trigger-path $TRIGGER_DIR',
        ]

        initialization_args = [ 
	    '--seed 28',
	    '--init-method-std 0.008944'
        ]

        learning_rate_args = [ 
	    '--lr 0.00015',
	    '--min-lr 0.000015',
	    '--lr-decay-style cosine',
	    '--lr-warmup-iters 200',
        ] 

        checkpoint_args = [ 
	    '--save $CKPT_DIR',
	    '--save-interval $CHECKPOINT_STEPS',
	    '--ckpt-format torch_dist',
	    '--load $CKPT_DIR',
	    '--async-save'
        ]

        mixed_precision_args = [
	    '--bf16'
        ]

        distributed_args = [ 
            f'--tensor-model-parallel-size {self.num_gpus_per_node}',
            f'--sequence-parallel',
            f'--pipeline-model-parallel-size 8',
            f'--num-layers-per-virtual-pipeline-stage 5',
            f'--context-parallel-size 1',
            f'--use-distributed-optimizer',
            f'--overlap-grad-reduce',
            f'--overlap-param-gather',
            f'--defer-embedding-wgrad-compute',
            f'--wgrad-deferral-limit 22',
            f'--overlap-p2p-communication-warmup-flush'
        ]

        tokenizer_args = [
	    '--tokenizer-type HuggingFaceTokenizer',
	    '--tokenizer-model alehc/swissai-tokenizer'
        ]

        data_args = [
	    f'--split 100,0,0',
	    f'--seq-length {self.sequence_length}',
	    f'--reset-position-ids',
	    f'--reset-attention-mask',
	    f'--eod-mask-loss',
	    f'--num-workers 1',
	    f'--num-dataset-builder-threads 1',
            f'--mock-data', # Try initially with mock data
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
     
        # Transformer Engine 
        self.executable_opts = [
            f"-c ", 
            f"'RANK=\$SLURM_PROCID LOCAL_RANK=\$SLURM_LOCALID {cmd_prefix} "
            f"{training_cmd}'"
        ]

    @sanity_function
    def assert_sanity(self):
        return True 

    @performance_function('GB/s')
    def bandwidth(self):
        return sn.extractsingle(r'\|\s*16GiB\s*\|\s*(?P<busbw>\S+)GBps\s*\|',
                                self.stdout, tag='busbw', conv=float
        )
