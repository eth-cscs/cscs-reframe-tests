# Copyright 2026 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
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
    num_tasks_per_node = 1

    default_num_nodes = variable(int, type(None), value=None)

    time_limit = '10m'

    # The LLM model to run
    model = parameter(['llama3-8b'])

    # Exit after iteration is divisible by the following number
    exit_interval = variable(int, value=1)

    # The checkpoint directory
    checkpoint_dir = variable(str, type(None), value=None)

    # The dataset_cache directory
    dataset_cache_dir = variable(str, type(None), value=None)

    # Enable NCCL Debug logging
    nccl_debug = variable(bool, value=False)

    # The number of checkpoint steps
    checkpoint_steps = variable(int, value=0)

    # The number of training steps
    training_steps = variable(int, value=5)

    configurations = {
        'llama3-8b': {
            'num_nodes': 2,
            'micro_batch_size': 1,
            'global_batch_size': 128,
            'sequence_length': 8192,
            'max_position_embeddings': 8192,
            'num_layers': 32,
            'hidden_size': 4096,
            'ffn_hidden_size': 14336,
            'num_attention_heads': 32,
            'tensor_model_parallel_size': 1,
            'context_model_parallel_size': 1,
            'pipeline_model_parallel_size': 1,

            'ref_throughput_per_gpu': 630.0,

            'dtype': 'fp8',
        }
    }

    sourcesdir = None
    executable = 'torchrun'

    @run_after('setup')
    def setup_test(self):
        descr = (
            'Megatron tests with synthetic data, with options for large scale '
            'and real data tests')
        model_config = self.configurations[self.model]
        if self.default_num_nodes is None:
            self.num_nodes = model_config['num_nodes']
        else:
            self.num_nodes = self.default_num_nodes

        curr_part = self.current_partition
        self.num_gpus_per_node = curr_part.select_devices('gpu')[0].num_devices
        self.num_tasks = self.num_nodes
        gpu_arch = curr_part.select_devices('gpu')[0].arch
        self.skip_if(
            gpu_arch != 'sm_90', 'test tuned only for 8xGH200'
        )
        self.num_cpus_per_task = model_config.get(
            'cpus_per_task', (curr_part.processor.num_cpus //
                              self.num_tasks_per_node)
        )
        self.reference = {
            '*': {
                'throughput_per_gpu':
                    (model_config['ref_throughput_per_gpu'], -0.1, None,
                     'TFLOP/s/GPU'),
            }
        }

    @run_after('setup')
    def set_executable_opts(self):
        model_config = self.configurations[self.model]
        self.env_vars = {
            'CUDA_DEVICE_MAX_CONNECTIONS': 1,
            'MASTER_ADDRESS': '$(srun -N1 hostname)',
            'MASTER_PORT': '28400',
            'WORLD_SIZE': f'{self.num_nodes * self.num_gpus_per_node}',
            'OMP_NUM_THREADS': '72'
        }

        if self.nccl_debug:
            self.env_vars['NCCL_DEBUG'] = 'Info'

        pretrain_script_path = '/workspace/Megatron-LM/pretrain_gpt.py'
        torchrun_args = [
            f'--nproc_per_node={self.num_gpus_per_node}',
            f'--nnodes={self.num_nodes}',
            '--rdzv-endpoint=$MASTER_ADDRESS:$MASTER_PORT',
            '--rdzv-backend=c10d',
        ]

        model_args = [
            '--use-mcore-models',
            f'--num-layers {model_config["num_layers"]}',
            f'--hidden-size {model_config["hidden_size"]}',
            f'--ffn-hidden-size {model_config["ffn_hidden_size"]}',
            f'--num-attention-heads {model_config["num_attention_heads"]}',
            '--group-query-attention',
            '--num-query-groups 8',
            '--kv-channels 128',
            f'--seq-length {model_config["sequence_length"]}',
            f'--max-position-embeddings {model_config["max_position_embeddings"]}',
            '--position-embedding-type rope',
            '--rotary-base 1000000',
            '--rotary-percent 1.0',
            '--attention-dropout 0.0',
            '--hidden-dropout 0.0',
            '--swiglu',
            '--init-method-std 0.0134',
            '--attention-backend fused',
            '--apply-layernorm-1p',
            '--untie-embeddings-and-output-weights',
            '--disable-bias-linear',
        ]

        training_args = [
            f'--micro-batch-size {model_config["micro_batch_size"]}',
            f'--global-batch-size {model_config["global_batch_size"]}',
            '--lr 0.00015',
            '--min-lr 0.00001',
            '--decoupled-lr 5.0e-4',
            '--decoupled-min-lr 4.5e-5',
            '--lr-decay-style cosine',
            '--clip-grad 1.0',
            '--weight-decay 0.1',
            '--adam-beta1 0.9',
            '--adam-beta2 0.95',
            '--bf16',
            '--grad-reduce-in-bf16',
            '--cross-entropy-loss-fusion',
            '--calculate-per-token-loss',
            '--manual-gc',
            '--empty-unused-memory-level 1',
            f'--train-iters {self.training_steps}',
            '--use-distributed-optimizer',
            '--overlap-grad-reduce',
            '--overlap-param-gather',
        ]

        dtype_args = []
        if model_config.get('dtype') == 'fp8':
            dtype_args = [
                '--fp8-format hybrid',
                '--fp8-amax-history-len 1024',
                '--fp8-amax-compute-algo max',
                '--fp8-param-gather',
            ]

        model_parallel_args = [
            f'--tensor-model-parallel-size {model_config["tensor_model_parallel_size"]}',
            f'--context-parallel-size {model_config.get("context_parallel_size", 1)}',
            '--sequence-parallel',
        ]

        data_args_list = [
            '--mock-data',
            '--tokenizer-type NullTokenizer',
            '--vocab-size 128256',
            '--data-cache-path /rfm_workdir/benchmark_cache_llama3_8b_fp8',
            '--tiktoken-pattern v2',
            '--split 99,1,0',
            '--no-create-attention-mask-in-dataloader',
            '--no-mmap-bin-files',
            '--num-workers 1',
        ]

        eval_and_logging_args = [
            '--log-interval 1',
            '--eval-iters 0',
            '--eval-interval 100',
            '--save-interval 1000',
            '--log-throughput',
            '--profile',
            '--profile-step-start 4',
            '--profile-step-end 6',
            '--ckpt-format torch_dist',
            '--distributed-timeout-minutes 60',
        ]

        self.executable_opts = [
            *torchrun_args,
            pretrain_script_path,
            *model_args,
            *training_args,
            *dtype_args,
            *model_parallel_args,
            *data_args_list,
            *eval_and_logging_args,
        ]

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r'\[after training is done\] datetime:',
                               self.stdout)

    @performance_function('TFLOP/s/GPU')
    def throughput_per_gpu(self):
        # Discard the first 2 iterations as warmup
        return sn.avg(sn.extractall(
            r'throughput per GPU \(TFLOP/s/GPU\):\s*(?P<throughput>\S+)',
            self.stdout, tag='throughput', conv=float
            )[2:]
        )


@rfm.simple_test
class PyTorchMegatronLM_CE_Dev(PyTorchMegatronLM, ContainerEngineMixin):
    valid_systems = ['+nvgpu +ce']
    valid_prog_environs = ['builtin']
    maintainers = ['VCUE']
    tags = {'ce_dev'}
    container_image = 'jfrog.svc.cscs.ch/ghcr/sarus-suite/containerfiles-ci/megatron-lm:0.15.2-pt25.11'

    @run_after('setup')
    def set_container_config(self):
        self.container_env_table = {
            'annotations.com.hooks': {
                'aws_ofi_nccl.enabled': 'true',
                'aws_ofi_nccl.variant': 'cuda-dl',
            },
        }


@rfm.simple_test
class PyTorchMegatronLM_Skybox(PyTorchMegatronLM_CE_Dev):
    tags = {'ce_dev', 'skybox'}

    @run_after('setup')
    def skip_test(self):
        self.skip('WIP. Requires specific functionality in default hooks and CDIs.')
