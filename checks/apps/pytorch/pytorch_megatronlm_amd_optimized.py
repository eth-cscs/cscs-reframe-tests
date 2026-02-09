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


class PyTorchMegatronLM_AMD_Optimized(rfm.RunOnlyRegressionTest):
    num_tasks_per_node = 1
    default_num_nodes = variable(int, type(None), value=None)
    time_limit = '60m'
    megatron_repo = variable(
        str, value='https://github.com/ROCm/Megatron-LM'
    )

    # FIXME: this PR needs to be merged so that the distributed
    # checkpointinting succeeds: https://github.com/ROCm/Megatron-LM/pull/83
    megatron_release = variable(str, value='38fc830')

    # The LLM model to run
    model = parameter(['llama3-8b'])
    # model = parameter(['llama3-70b'])
    exit_interval = variable(int, value=10)
    checkpoint_dir = variable(str, type(None), value=None)
    dataset_cache_dir = variable(str, type(None), value=None)
    enable_fp8 = variable(bool, value=False)
    sequence_parallel = variable(bool, value=True)
    gemm_tuning = variable(bool, value=True)
    mcore = variable(bool, value=True)
    conti_params = variable(bool, value=False)
    fsdp = variable(bool, value=False)
    use_flash_attn = variable(bool, value=True)
    rope_fusion = variable(bool, value=True)
    eval_interval = variable(int, value=5000)
    save_interval = variable(int, value=5000)
    eval_iters = variable(int, value=1)
    recompute = variable(bool, value=False)
    nccl_debug = variable(bool, value=False)
    batch_size_per_node = variable(int, value=256)
    checkpoint_steps = variable(int, value=10)
    hf_home = variable(
        str, value=str(pathlib.Path(os.environ['SCRATCH']) / '.cache' / 'huggingface')
    )
    training_steps = variable(int, value=10)
    wandb_logging = variable(bool, value=False)
    datasets = variable(str, type(None), value=None)

    configurations = {
        'llama3-8b': {
            'num_nodes': 16,
            'micro_batch_size': 1,
            'global_batch_size': 512,
            'sequence_length': 8192,
            'num_layers': 32,
            'hidden_size': 4096,
            'ffn_hidden_size': 14336,
            'num_attention_heads': 32,
            'tensor_model_parallel_size': 1,
            'pipeline_model_parallel_size': 1,
            'context_parallel_size': 1,
            'activation': 'swiglu',
            'optimizer': 'adam',
            'regularization_args': [
                '--attention-dropout 0.0',
                '--hidden-dropout 0.0',
                '--weight-decay 0.1',
                '--clip-grad 1.0',
                '--adam-beta1 0.9',
                '--adam-beta2 0.95',
            ],
            'learning_rate_args': [
                f'--lr 1.e-4',
                f'--min-lr 1.e-5',
                f'--lr-decay-style cosine',
                f'--lr-warmup-iters 1',
            ]
        },
        'llama3-70b': {
            'num_nodes': 32,
            'micro_batch_size': 1,
            'global_batch_size': 1024,
            'sequence_length': 8192,
            'num_layers': 80,
            'hidden_size': 8192,
            'ffn_hidden_size': 28672,
            'num_attention_heads': 64,
            'tensor_model_parallel_size': 4,
            'pipeline_model_parallel_size': 8,
            'context_parallel_size': 1,
            'activation': 'swiglu',
            'optimizer': 'adam',
            'regularization_args': [
                '--attention-dropout 0.0',
                '--hidden-dropout 0.0',
                '--weight-decay 0.1',
                '--clip-grad 1.0',
                '--adam-beta1 0.9',
                '--adam-beta2 0.95',
            ],
            'learning_rate_args': [
                f'--lr 1.e-4',
                f'--min-lr 1.e-5',
                f'--lr-decay-style cosine',
                f'--lr-warmup-iters 1',
            ]
        }
    }

    sourcesdir = None
    executable = 'bash'

    maintainers = ['VCUE', 'SSA']
    tags = {'ml', 'bencher'}

    @run_after('setup')
    def setup_test(self):
        model_config = self.configurations[self.model]
        if self.default_num_nodes is None:
            self.num_nodes = model_config['num_nodes']
        else:
            self.num_nodes = self.default_num_nodes

        curr_part = self.current_partition
        self.num_gpus_per_node = curr_part.select_devices('gpu')[0].num_devices
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        gpu_arch = curr_part.select_devices('gpu')[0].arch
        self.skip_if(
            gpu_arch != 'gfx942', 'test valid only for AMD MI300'
        )
        self.num_cpus_per_task = model_config.get(
            'cpus_per_task', (curr_part.processor.num_cpus //
                              curr_part.processor.num_cpus_per_core)
        )
        self.reference = {
            '*': {
                'throughput_per_gpu':
                    (0.0, None, None, 'TFLOP/s/GPU'),
            }
        }

    @run_after('setup')
    def set_executable_opts(self):
        model_config = self.configurations[self.model]
        self.env_vars = {
            'CUDA_DEVICE_MAX_CONNECTIONS': 1,
            'GPU_MAX_HW_QUEUES': 2,
            'TORCH_NCCL_HIGH_PRIORITY': 1,
            'MASTER_ADDR': '$(hostname)',
            'MASTER_PORT': '29400',
            'WORLD_SIZE': '$SLURM_NPROCS',
            'AITER_ROOT_DIR': '$SCRATCH/.aiter',
            'AITER_JIT_DIR': '$AITER_ROOT_DIR/jit',
            'MEGATRON_LM_DIR': '$PWD/Megatron-LM',
            'PYTHONPATH': '$MEGATRON_LM_DIR:$PYTHONPATH',
            'NCCL_TUNER_CONFIG_FILE': '/capstor/store/cscs/cscs/public/reframe/resources/rccl-tuner/nccl_tuner.conf',
            'NCCL_TUNER_PLUGIN': '/capstor/store/cscs/cscs/public/reframe/resources/rccl-tuner/libnccl-tuner.so',
            'NCCL_TUNER_PLUGIN_SAVE_REQUESTS': 'TRUE',
            'PROJECT_NAME':
                f'Megatron-{self.current_system.name.capitalize()}',
            'EXP_NAME': f'{self.model}-$SLURM_NNODES-nodes',
            'PROJECT_DIR': '$MEGATRON_LM_DIR/logs/Meg-Runs/$PROJECT_NAME',
            'EXP_DIR': '$PROJECT_DIR/$EXP_NAME',
            'CKPT_DIR': self.checkpoint_dir or '$EXP_DIR/checkpoints',
            'DEBUG_DIR': '$EXP_DIR/debug/$SLURM_JOB_ID',
            'COMPUTE_ENVIRONMENT_DIR': '$DEBUG_DIR/compute_environment.txt',
            'GPU_MEM_LOGGING': '$DEBUG_DIR/memory_logging.txt',
            'LOGGING_DIR': '$EXP_DIR/logging',
            'TENSORBOARD_DIR': '$LOGGING_DIR/tensorboard',
            'BACKUP_CODEBASE_DIR': '$EXP_DIR/Megatron-LM',
            'DATASET_CACHE_DIR': (self.dataset_cache_dir or
                                  '$PWD/datasets/cache'),
            'HF_HOME': f'{self.hf_home}',
            'OMP_NUM_THREADS': self.num_cpus_per_task // self.num_gpus_per_node,
            # Libfabric optimizations
            'NCCL_CROSS_NIC': 1,
            'NCCL_NET': '"AWS Libfabric"',
            'NCCL_NET_GDR_LEVEL': 'PHB',
            'NCCL_PROTO': '^LL128',
            'FI_CXI_DEFAULT_CQ_SIZE': 131072,
            'FI_CXI_DEFAULT_TX_SIZE': 32768,
            'FI_CXI_DISABLE_HOST_REGISTER': 1,
            'FI_MR_CACHE_MONITOR': 'userfaultfd',
            'FI_CXI_RDZV_EAGER_SIZE': 0,
            'FI_CXI_RDZV_GET_MIN': 0,
            'FI_CXI_RDZV_THRESHOLD': 0,
            'HSA_NO_SCRATCH_RECLAIM': 1,
        }

        if self.gemm_tuning:
            self.env_vars['TE_HIPBLASLT_TUNING_RUN_COUNT'] = 10
            self.env_vars['TE_HIPBLASLT_TUNING_ALGO_COUNT'] = 100

        if self.nccl_debug:
            self.env_vars['NCCL_DEBUG'] = 'Info'

        self.prerun_cmds = [
            f'set -x',

            # Download tokenizer model
            f'mkdir -p tokenizer',
            f'cd tokenizer',
            f'wget https://huggingface.co/NousResearch/Llama-2-7b-chat-hf/resolve/main/tokenizer.model',  # noqa E262
            f'cd -',

            # Clone Megatron repo
            f'git clone {self.megatron_repo} $MEGATRON_LM_DIR',
            f'cd $MEGATRON_LM_DIR',
            f'git fetch origin',
            f'git checkout {self.megatron_release}',
            f'cd -',

            # Create the corresponding dirs
            f'echo "START TIME: $(date)"',
            f'ulimit -c 0',
            f'mkdir -p $HF_HOME',
            f'mkdir -p $CKPT_DIR',
            f'mkdir -p $PROJECT_DIR',
            f'mkdir -p $DEBUG_DIR',
            f'mkdir -p $LOGGING_DIR',
        ]

        self.postrun_cmds = ['echo "END TIME: $(date)"']
        logging_args = []
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

        distributed_args = [
            f'--use-distributed-optimizer',
            f'--overlap-grad-reduce',
            f'--overlap-param-gather',
            f'--distributed-backend nccl',
            f'--distributed-timeout-minutes 120',
        ]

        gpt_args = [
            f'--tensor-model-parallel-size '
            f'{model_config["tensor_model_parallel_size"] or self.num_gpus_per_node}',  # noqa E262
            f'--pipeline-model-parallel-size '
            f'{model_config["pipeline_model_parallel_size"]}',
            f'--context-parallel-size ',
            f'{model_config["context_parallel_size"]}',
            f'--num-layers {model_config["num_layers"]}',
            f'--hidden-size {model_config["hidden_size"]}',
            f'--ffn-hidden-size {model_config["ffn_hidden_size"]}',
            f'--num-attention-heads {model_config["num_attention_heads"]}',
            f'--max-position-embeddings {model_config["sequence_length"]}',
            f'--untie-embeddings-and-output-weights',
            f'--position-embedding-type rope',
            f'--no-position-embedding',
            f'--micro-batch-size {model_config["micro_batch_size"]}',
            f'--global-batch-size {model_config["global_batch_size"]}',
            f'--no-check-for-nan-in-loss-and-grad',
            f'--train-iters {self.training_steps}',
            f'--group-query-attention',
            f'--num-query-groups 8',
            f'--no-gradient-accumulation-fusion',
            f'--normalization RMSNorm',
            f'--no-async-tensor-model-parallel-allreduce',
            f'--no-masked-softmax-fusion',
            f'--disable-bias-linear',
            f'--optimizer {model_config["optimizer"]}',
            f'--exit-signal-handler',
        ]

        if self.recompute:
            gpt_args += [
                f'--recompute-num-layers {model_config["num_layers"]}',
                f'--recompute-granularity full',
                f'--recompute-method block'
            ]

        if self.use_flash_attn:
            gpt_args += [
                '--use-flash-attn'
            ]

        if not self.rope_fusion:
            gpt_args += [
                '--no-rope-fusion'
            ]

        if self.sequence_parallel:
            gpt_args += [
                '--sequence-parallel'
            ]

        if self.mcore:
            gpt_args += [
                '--use-mcore-models'
            ]

        if self.conti_params:
            gpt_args += [
                '--use-contiguous-parameters-in-local-ddp'
            ]

        fp8_args = []
        if self.enable_fp8:
            fp8_args += [
                '--transformer-impl=transformer_engine',
                '--fp8-margin=0',
                '--fp8-format=hybrid',
                '--fp8-interval=1',
                '--fp8-amax-history-len=1024',
                '--fp8-amax-compute-algo=max',
                '--attention-softmax-in-fp32'
            ]

        initialization_args = [
            '--init-method-std 0.02'
        ]

        output_args = [
            f'--log-interval 1',
            f'--log-progress',
            f'--log-throughput',
            f'--no-save-optim',
            f'--no-save-rng',
            f'--eval-iters {self.eval_iters}',
            f'--exit-interval={self.exit_interval}',
        ]

        checkpoint_args = [
            f'--save $CKPT_DIR',
            f'--save-interval {self.checkpoint_steps}',
            f'--ckpt-format torch_dist',
            f'--ckpt-fully-parallel-load',
            f'--load $CKPT_DIR',
            f'--async-save'
        ]

        mixed_precision_args = [
            '--bf16'
        ]

        tokenizer_args = [
            f'--tokenizer-type Llama2Tokenizer',
            f'--tokenizer-model {self.stagedir}/tokenizer/tokenizer.model'
        ]

        data_args = [
            f'--split 99990,8,2',
            f'--dataloader-type cyclic',
            f'--seq-length {model_config["sequence_length"]}',
            f'--num-workers '
            f'{self.num_cpus_per_task // self.num_gpus_per_node}',
            f'--num-dataset-builder-threads 8',
        ]

        if self.datasets is None:
            data_args += ['--mock-data']
        else:
            data_args += [
                '--data-path $DATAPATH_CONFIGURED',
                '--data-cache-path $DATASET_CACHE_DIR'
            ]

        all_args = [
            *gpt_args,
            *model_config['regularization_args'],
            *fp8_args,
            *initialization_args,
            *model_config['learning_rate_args'],
            *output_args,
            *checkpoint_args,
            *mixed_precision_args,
            *distributed_args,
            *tokenizer_args,
            *data_args,
            *logging_args
        ]

        training_cmd = (
            f'export NCCL_TUNER_TUNING_FILE=$SCRATCH/rccl-tuner/logs/$SLURM_PROCID.csv \n'
            f'mkdir -p $SCRATCH/rccl-tuner/logs \n'
            f'torchrun  '
            f'--nproc_per_node {self.num_gpus_per_node} '
            f'--nnodes {self.num_nodes} '
            f'--master_addr $MASTER_ADDR '
            f'--master_port $MASTER_PORT '
            f'--node_rank=$SLURM_PROCID '
            f'$MEGATRON_LM_DIR/pretrain_gpt.py {" ".join(all_args)}'
        )

        self.executable_opts = [
            rf"-c",

            # Open-close with single quotes
            rf"'{training_cmd}'"
        ]

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r'\[exiting program at iteration \d+\]',
                               self.stdout)

    @performance_function('TFLOP/s/GPU')
    def throughput_per_gpu(self):
        return sn.avg(sn.extractall(
            r'throughput per GPU \(TFLOP/s/GPU\):\s*(?P<throughput>\S+)',
            self.stdout, tag='throughput', conv=float
        ))

class pytorch_image_import(rfm.RunOnlyRegressionTest):
    sourcesdir = None
    image = variable(
        str,
        value=('docker://rocm/megatron-lm:v25.5_py312')
    )
    archive_name = 'pytorch.sqsh'
    executable = 'enroot'
    valid_systems = ['+ce']
    valid_prog_environs = ['builtin']

    @run_before('run')
    def set_job_options(self):
        self.job.options = ['--partition=mi300']

    @run_before('run')
    def set_executable_opts(self):
        self.executable_opts = ['import', '-o', self.archive_name, self.image]

    @sanity_function
    def assert_image_imported(self):
        return sn.path_exists(os.path.join(self.stagedir, self.archive_name))

@rfm.simple_test
class PyTorchMegatronLM_AMD_Optimized_CE(PyTorchMegatronLM_AMD_Optimized, ContainerEngineMixin):
    valid_systems = ['+amdgpu +ce']
    valid_prog_environs = ['builtin']
    maintainers = ['VCUE', 'SSA']
    pytorch_image = fixture(pytorch_image_import, scope='session')

    @run_after('setup')
    def set_container_config(self):
        self.container_image = os.path.join(self.pytorch_image.stagedir,
                                            self.pytorch_image.archive_name)
        self.container_env_table = {
            'annotations.com.hooks': {
                'aws_ofi_nccl.enabled': 'true',
                'aws_ofi_nccl.variant': 'rocm6',
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

        self.container_mounts += [f'{self.hf_home}:{self.hf_home}']

        if self.dataset_cache_dir:
            self.container_mounts += [
                f'{self.dataset_cache_dir}:{self.dataset_cache_dir}'
            ]

        if self.checkpoint_dir:
            self.container_mounts += [
                f'{self.checkpoint_dir}:{self.checkpoint_dir}'
            ]
