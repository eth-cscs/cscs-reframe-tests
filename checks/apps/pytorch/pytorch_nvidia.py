import sys
import pathlib
import reframe as rfm
import reframe.utility.sanity as sn



from pytorch_test_base import PyTorchTestBase
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from container_engine import ContainerEngineMixin  # noqa: E402

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.parent / 'utility'))
from nvidia_nvcr.nvcr_utility import latest_nvidia_image_tags



@rfm.simple_test
class test_image_latest_tag_retreival(rfm.RunOnlyRegressionTest):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['builtin']
    executable = 'echo'

    @sanity_function
    def validate(self):
        return sn.assert_found(r'latest tags:', self.stdout)
    
    @run_before('run')
    def set_container_variables(self):
        self.executable_opts = ["latest tags:" + ",".join(latest_nvidia_image_tags("pytorch"))]


@rfm.simple_test
class PyTorchDdpCeNv(PyTorchTestBase, ContainerEngineMixin):
    descr = 'Check the training throughput using the ContainerEngine and NVIDIA NGC'
    valid_systems = ['+ce +nvgpu']
    aws_ofi_nccl = parameter([True])
    curated_images = [
        #'nvcr.io#nvidia/pytorch:22.08-py3', # same as AMD   pt1.13.1
        #'nvcr.io#nvidia/pytorch:22.12-py3', # same as Sarus pt1.14.0
        #'nvcr.io#nvidia/pytorch:23.10-py3', # same as AMD   pt2.1.0
        'nvcr.io#nvidia/pytorch:24.01-py3', # Latest        pt2.2.0
    ]
    latest_images = ["nvcr.io#nvidia/pytorch:" + tag for tag in latest_nvidia_image_tags("pytorch")]
    image = parameter(curated_images + latest_images)

    env_vars = {
        'NCCL_DEBUG': 'Info',
    }
    tags = {'production', 'ce'}

    @run_after('init')
    def set_image(self):
        self.container_image = self.image
        if self.aws_ofi_nccl:
            cuda_major = 'cuda12' if self.image > 'nvcr.io#nvidia/pytorch:23' else 'cuda11'
            self.container_env_table = {
                'annotations.com.hooks': {
                    'aws_ofi_nccl.enabled': 'true',
                    'aws_ofi_nccl.variant': cuda_major,
                },
            }

@rfm.simple_test
class PyTorchDdpCeNvlarge(PyTorchDdpCeNv):
    aws_ofi_nccl = parameter([True, False])
    num_nodes = parameter([3, 8])

    curated_images = [
        'nvcr.io#nvidia/pytorch:24.01-py3', # Latest        pt2.2.0
    ]
    latest_images = ["nvcr.io#nvidia/pytorch:" + tag for tag in latest_nvidia_image_tags("pytorch")]
    image = parameter(curated_images + latest_images)


# DISABLED - lib comatibility issue on Clariden
# + srun -l --gpus-per-task=1 python cnn_distr.py
# srun: /lib64/libc.so.6: version `GLIBC_2.34' not found (required by /opt/cscs/aws-ofi-ccl-plugin/cuda12/libnccl-net.so)
# TODO: build libnccl-net.so plug-in in the test setup pahse
@rfm.simple_test
class PyTorchDdpMambaNv(PyTorchTestBase):
    descr = 'Check the training throughput on bare-metal'
    valid_systems = []  #DISABLED TEST, change to ['+nvgpu'] to renable it
    time_limit = '30m'
    torch_version = parameter([
        #'pytorch torchvision nccl pytorch-cuda=11.8', # Latest cu11.8; aws-ofi-ccl-plugin/cuda11 not available
         'nccl cuda=12.6', # Latest cu12.6; incompatible driver
    ])
    tags = {'production'}

    @run_after('setup')
    def activate_venv(self):
        self.prerun_cmds = [
            f'set -xe', f'. setup_conda.sh $PWD/forge',
            f'conda update -n base -c conda-forge conda',
            f'conda clean --all',
            f'conda create -p $PWD/forge/envs/rfm {self.torch_version} '
            f'-c nvidia -y',
            f'conda activate $PWD/forge/envs/rfm',
            f'pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126',
            f'pip install python-hostlist',
            f'. activate_ofi.sh cuda12',
        ]

        self.postrun_cmds = ['rm Miniforge*.sh', 'rm -rf forge']
