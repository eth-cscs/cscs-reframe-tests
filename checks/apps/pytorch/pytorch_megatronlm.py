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

    default_num_nodes = variable(int, type(None), value=None)

    time_limit = '20m'

    # The Megatron repository and release/commit to use.
    megatron_repo = variable(
        str, value='https://github.com/swiss-ai/Megatron-LM.git'
    )
    megatron_release = variable(str, value='de14c22')

    # The LLM model to run
    model = parameter(['llama3-8b', 'llama3-70b'])

    # Exit after iteration is divisible by the following number
    exit_interval = variable(int, value=10)

    # The checkpoint directory
    checkpoint_dir = variable(str, type(None), value=None)

    # The dataset_cache directory
    dataset_cache_dir = variable(str, type(None), value=None)

    # Enable NCCL Debug logging
    nccl_debug = variable(bool, value=False)

    # The number of checkpoint steps
    checkpoint_steps = variable(int, value=10)

    hf_home = variable(
        str, value=str(pathlib.Path.home() / '.cache' / 'huggingface')
    )

    # The number of training steps
    training_steps = variable(int, value=50)

    # Use WANDB logging
    wandb_logging = variable(bool, value=False)

    # The dataset paths to use.
    # Multiple paths can be passed using ',' as path separator.
    # Mock data is going to be used if the value is `None`.
    datasets = variable(str, type(None), value=None)

    configurations = {
        'apertus3-70b': {
            'num_nodes': 512,
            'cpus_per_task': 36,
            'micro_batch_size': 1,
            'global_batch_size': 2048,
            'sequence_length': 4096,
            'num_layers': 80,
            'hidden_size': 8192,
            'ffn_hidden_size': 43008,
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
            'overlap_p2p_communication_warmup_flush': True,

            'ref_tokens_per_sec_per_gpu': 700.0,
            'ref_throughput_per_gpu': 330.0,

            'activation': 'xielu',
            'optimizer': 'ademamix',
            'transformer_engine_args': [
                '--main-grads-dtype fp32'
            ],
            'extra_network_size_args': [
                '--qk-layernorm',
                '--qknorm-impl apex',
            ],
            'regularization_args': [
                '--attention-dropout 0.0',
                '--hidden-dropout 0.0',
                '--weight-decay 0.1',
                '--clip-grad 0.1',
                '--adam-beta1 0.9',
                '--adam-beta2 0.999',
                '--ademamix-alpha 8',
                '--ademamix-beta3 0.9999',
                '--ademamix-beta3-warmup 100000',
                '--ademamix-alpha-warmup 100000',
            ],
            'learning_rate_args': [
                '--lr 0.00001',
                '--min-lr 0.000001',
                '--lr-decay-style WSD',
                '--lr-warmup-iters 2000',
                '--lr-wsd-decay-style 1-sqrt',
                '--lr-wsd-decay-iters 0',
            ],
            'extra_data_args': [
                '--num-workers 32',
                '--num-dataset-builder-threads 8',
                '--goldfish-loss',
                '--goldfish-k 50',
                '--goldfish-h 50',
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
            'overlap_p2p_communication_warmup_flush': True,

            'ref_tokens_per_sec_per_gpu': 850.0,
            'ref_throughput_per_gpu': 410.0,

            'activation': 'swiglu',
            'optimizer': 'adam',
            'transformer_engine_args': [
                '--transformer-impl transformer_engine',
                '--use-precision-aware-optimizer',
                '--main-grads-dtype bf16'
            ],
            'regularization_args': [
                '--attention-dropout 0.0',
                '--hidden-dropout 0.0',
                '--weight-decay 0.1',
                '--clip-grad 1.0',
                '--adam-beta1 0.9',
                '--adam-beta2 0.95',
            ],
            'learning_rate_args': [
                f'--lr 0.000015',
                f'--min-lr 0.000015',
                f'--lr-decay-style cosine',
                f'--lr-warmup-iters 1',
            ],
            'extra_data_args': [
                '--num-workers 32',
                '--num-dataset-builder-threads 8',
            ]
        },
        'llama3-8b': {
            'num_nodes': 16,
            'micro_batch_size': 1,
            'global_batch_size': 128,
            'sequence_length': 8192,
            'num_layers': 32,
            'hidden_size': 4096,
            'ffn_hidden_size': 14336,
            'num_attention_heads': 32,
            'tensor_model_parallel_size': 1,
            'pipeline_model_parallel_size': 1,
            'manual_gc_interval': '500',
            'sequence_parallel': False,
            'defer_embedding_wgrad_compute': False,
            'overlap_p2p_communication_warmup_flush': False,

            'ref_tokens_per_sec_per_gpu': 7000.0,
            'ref_throughput_per_gpu': 400.0,

            'activation': 'swiglu',
            'optimizer': 'adam',
            'transformer_engine_args': [
                '--transformer-impl transformer_engine',
                '--use-precision-aware-optimizer',
                '--main-grads-dtype bf16'
            ],
            'regularization_args': [
                '--attention-dropout 0.0',
                '--hidden-dropout 0.0',
                '--weight-decay 0.1',
                '--clip-grad 1.0',
                '--adam-beta1 0.9',
                '--adam-beta2 0.95',
            ],
            'learning_rate_args': [
                f'--lr 0.00022',
                f'--min-lr 0.000022',
                f'--lr-decay-style cosine',
                f'--lr-warmup-iters 1',
            ],
            'extra_data_args': [
                '--num-workers 32',
                '--num-dataset-builder-threads 8',
            ]
        }
    }

    sourcesdir = None
    executable = 'bash'

    tags = {'maintenance', 'production', 'ml'}

    @run_after('setup')
    def setup_test(self):
        model_config = self.configurations[self.model]
        if self.default_num_nodes is None:
            self.num_nodes = model_config['num_nodes']
        else:
            self.num_nodes = self.default_num_nodes

        curr_part = self.current_partition
        self.num_gpus_per_node = curr_part.select_devices('gpu')[0].num_devices
        self.num_tasks = self.num_nodes * self.num_gpus_per_node
        self.num_cpus_per_task = model_config.get(
            'cpus_per_task', (curr_part.processor.num_cpus //
                              self.num_tasks_per_node)
        )
        self.reference = {
            '*': {
                'throughput_per_gpu':
                    (model_config['ref_throughput_per_gpu'], -0.1, None,
                     'TFLOP/s/GPU'),
                'tokens_per_sec_per_gpu':
                    (model_config['ref_tokens_per_sec_per_gpu'], -0.1, None,
                     'tokens/sec/gpu'),
            }
        }

    @run_after('setup')
    def set_executable_opts(self):
        model_config = self.configurations[self.model]
        self.env_vars = {
            'TORCH_NCCL_AVOID_RECORD_STREAMS': 1,
            'TORCH_NCCL_ASYNC_ERROR_HANDLING': 1,
            'CUDA_DEVICE_MAX_CONNECTIONS': 1,
            'MASTER_ADDR': '$(hostname)',
            'MASTER_PORT': '29400',
            'WORLD_SIZE': '$SLURM_NPROCS',
            'MEGATRON_LM_DIR': '$PWD/Megatron-LM',
            'PYTHONPATH': '$MEGATRON_LM_DIR:$PYTHONPATH',
            'PROJECT_NAME':
                f'Megatron-{self.current_system.name.capitalize()}',
            'EXP_NAME': f'{self.model}-$SLURM_NNODES-nodes',
            'PROJECT_DIR': '$MEGATRON_LM_DIR/logs/Meg-Runs/$PROJECT_NAME',
            'EXP_DIR': '$PROJECT_DIR/$EXP_NAME',
            'CKPT_DIR': self.checkpoint_dir or '$EXP_DIR/checkpoints',
            'TRIGGER_DIR': '$EXP_DIR/triggers',
            'DEBUG_DIR': '$EXP_DIR/debug/$SLURM_JOB_ID',
            'COMPUTE_ENVIRONMENT_DIR': '$DEBUG_DIR/compute_environment.txt',
            'GPU_MEM_LOGGING': '$DEBUG_DIR/memory_logging.txt',
            'LOGGING_DIR': '$EXP_DIR/logging',
            'TENSORBOARD_DIR': '$LOGGING_DIR/tensorboard',
            'BACKUP_CODEBASE_DIR': '$EXP_DIR/Megatron-LM',
            'DATASET_CACHE_DIR': (self.dataset_cache_dir or
                                  '$PWD/datasets/cache'),
            'HF_HOME': f'{self.hf_home}',
            'OMP_NUM_THREADS': self.num_cpus_per_task // self.num_gpus_per_node
        }

        if self.nccl_debug:
            self.env_vars['NCCL_DEBUG'] = 'Info'

        self.prerun_cmds = [
            f'set -x',
            f'git clone {self.megatron_repo} $MEGATRON_LM_DIR',
            f'cd $MEGATRON_LM_DIR',
            f'git fetch origin',
            f'git checkout {self.megatron_release}',
            f'cd -',
            f'echo "START TIME: $(date)"',
            f'ulimit -c 0',
            f'mkdir -p $HF_HOME',
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
            f'--{model_config["activation"]}',
            f'--untie-embeddings-and-output-weights',
        ]

        network_size_args += model_config.get('extra_network_size_args', [])

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

        training_args = [
            f'--micro-batch-size {model_config["micro_batch_size"]}',
            f'--global-batch-size {model_config["global_batch_size"]}',
            f'--no-check-for-nan-in-loss-and-grad',
            f'--train-iters {self.training_steps}',
            f'--log-interval 1',
            f'--eval-iters 0',
            f'--exit-interval={self.exit_interval}',
            f'--cross-entropy-loss-fusion',
            # Test this for latency
            f'--ddp-bucket-size 10000000000',
            f'--disable-bias-linear',
            f'--optimizer {model_config["optimizer"]}',
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

        distributed_args = [
            f'--tensor-model-parallel-size '
            f'{model_config["tensor_model_parallel_size"] or self.num_gpus_per_node}',  # noqa E262
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
        ]

        data_args += model_config.get('extra_data_args', [])

        if self.datasets is None:
            data_args += ['--mock-data']
        else:
            data_args += [
                '--data-path $DATAPATH_CONFIGURED',
                '--data-cache-path $DATASET_CACHE_DIR'
            ]

        all_args = [
            *model_config['transformer_engine_args'],
            *network_size_args,
            *logging_args,
            *model_config['regularization_args'],
            *training_args,
            *initialization_args,
            *model_config['learning_rate_args'],
            *checkpoint_args,
            *mixed_precision_args,
            *distributed_args,
            *tokenizer_args,
            *data_args
        ]

        training_cmd = (
            f'python $MEGATRON_LM_DIR/pretrain_gpt.py {" ".join(all_args)}'
        )

        cmd_prefix = ''
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
        return sn.assert_found(r'\[exiting program at iteration \d+\]',
                               self.stdout)

    @performance_function('tokens/sec/gpu')
    def tokens_per_sec_per_gpu(self):
        return sn.avg(
            sn.extractall(r'tokens/sec/gpu:\s*(?P<tokens>\S+)',
                          self.stdout, tag='tokens', conv=float)
        )

    @performance_function('TFLOP/s/GPU')
    def throughput_per_gpu(self):
        return sn.avg(sn.extractall(
            r'throughput per GPU \(TFLOP/s/GPU\):\s*(?P<throughput>\S+)',
            self.stdout, tag='throughput', conv=float
        ))


class pytorch_image_import(rfm.RunOnlyRegressionTest):
    image = variable(
        str,
        value=('docker://jfrog.svc.cscs.ch#reframe-oci/'
               'pytorch:25.01-py3_nvrtc-12.9')
    )
    archive_name = 'pytorch.sqsh'
    executable = 'enroot'
    valid_systems = ['+ce']
    valid_prog_environs = ['builtin']

    @run_before('run')
    def set_executable_opts(self):
        self.executable_opts = ['import', '-o', self.archive_name, self.image]

    @sanity_function
    def assert_image_imported(self):
        return sn.path_exists(os.path.join(self.stagedir, self.archive_name))


@rfm.simple_test
class PyTorchMegatronLM_CE(PyTorchMegatronLM, ContainerEngineMixin):
    valid_systems = ['+nvgpu +ce']
    valid_prog_environs = ['builtin']
    pytorch_image = fixture(pytorch_image_import, scope='session')

    @run_after('setup')
    def set_container_config(self):
        self.container_image = os.path.join(self.pytorch_image.stagedir,
                                            self.pytorch_image.archive_name)
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

        self.container_mounts += [f'{self.hf_home}:{self.hf_home}']

        if self.dataset_cache_dir:
            self.container_mounts += [
                f'{self.dataset_cache_dir}:{self.dataset_cache_dir}'
            ]

        if self.checkpoint_dir:
            self.container_mounts += [
                f'{self.checkpoint_dir}:{self.checkpoint_dir}'
            ]


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


@rfm.simple_test
class PyTorchMegatronLM_CE_apertus70b(PyTorchMegatronLM_CE):
    tags = {'ml'}
    model = parameter(['apertus3-70b'])
    time_limit = '30m'
