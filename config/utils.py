import re
from collections import defaultdict
from utilities.constants import *
import subprocess
import logging
from contextlib import contextmanager
import os

# Define a custom logging format with colors
class CustomFormatter(logging.Formatter):
    # Define log format
    format = "%(message)s"

    # Define ANSI escape codes for colors
    RESET = "\033[0m"
    COLORS = {
        logging.DEBUG: "",  # No color for DEBUG
        logging.INFO: "\033[32m",  # Green for INFO
        logging.WARNING: "\033[33m",  # Yellow for WARNING
        logging.ERROR: "\033[31m",  # Red for ERROR
        logging.CRITICAL: "\033[31;1m"  # Bright Red for CRITICAL
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


def parse_devices_output(file_path):

    gpu_info = defaultdict(lambda: {})
    nvidia_gpus_found = False

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        # Check for NVIDIA GPUs
        if "NVIDIA GPUs installed" in line:
            nvidia_gpus_found = True
        elif line == "\n" or "Batch Job Summary" in line:
            nvidia_gpus_found = False
            break
        elif nvidia_gpus_found:
            model = [gpu_m for gpu_m in nvidia_gpu_architecture if gpu_m in line]
            if not model:
                break
            elif len(model) > 1:
                pass
            else:
                model = model[0]
            if model not in gpu_info["NVIDIA"]:
                gpu_info["NVIDIA"].update({model : 1})
            else:
                gpu_info["NVIDIA"][model] += 1

        # Check for AMD GPUs
        elif "AMD" in line or "Radeon" in line:
            match = re.search(r'(\w+ \w+)', line)
            if match:
                model = match.group(0).strip()
                if model not in gpu_info["AMD"]:
                    gpu_info["AMD"].update({model : 1})
                else:
                    gpu_info["AMD"][model] += 1

        # Check for Intel GPUs
        elif "Intel" in line:
            match = re.search(r'(\w+ \w+)', line)
            if match:
                model = match.group(0).strip()
                if model not in gpu_info["Intel"]:
                    gpu_info["Intel"].update({model : 1})
                else:
                    gpu_info["Intel"][model] += 1

    return gpu_info

def parse_containers_output(file_path : str):

    containers_info = []
    containers_found = False

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if "Installed containers" in line:
            containers_found = True
        elif "GPU" in line or line == "\n" or "Batch Job Summary" in line:
            containers_found = False
            break
        elif containers_found:
            type = line.split(' modules: ')[0].strip()
            try:
                modules = line.split(' modules: ')[1].split(', ')
                modules = [m.strip() for m in modules]
                modules.append(type.lower())
            except:
                modules = []
            containers_info.append({'type': type, 'modules': modules})

    return containers_info


def parse_cnmemory_output(file_path : str):

    cnmemory_info = None
    cnmemory_found = False

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if "Total memory:" in line:
            match = re.search(r'(\d+)Gi', line)
            if match:
                cnmemory_info = match.group(1)
                break

    return cnmemory_info


def generate_submission_file(containers : bool, devices : bool, cn_memory : bool, partition_name : str, access : list = []):

    with open(f"autodetection_{partition_name}.sh", "w") as file:
        # Write some text to the file
        file.write(slurm_submission_header.format(partition_name=partition_name))
        for access_option in access:
            file.write(f"#SBATCH {access_option}\n")
        if containers:
            file.write(containers_detect_bash)
        file.write("\n")
        file.write("\n")
        if devices:
            file.write(devices_detect_bash)
        file.write("\n")
        file.write("\n")
        if cn_memory:
            file.write(cn_memory_bash)


def extract_info(containers : bool, devices : bool, cn_memory : bool, partition_name : str):

    containers_info, devices_info, cnmemory_info = [], [], []

    if containers:
        containers_info = parse_containers_output(f"config_autodetection_{partition_name}.out")
        # containers_info = parse_containers_output(f"config_autodetection_normal copy.out")
    if devices:
        devices_info = parse_devices_output(f"config_autodetection_{partition_name}.out")
        # devices_info = parse_devices_output(f"config_autodetection_normal copy.out")
    if cn_memory:
        cnmemory_info = parse_cnmemory_output(f"config_autodetection_{partition_name}.out")
        # cnmemory_info = parse_cnmemory_output(f"config_autodetection_normal copy.out")

    return containers_info, devices_info, cnmemory_info


def submit_autodetection(partition_name):

    cmd_parts = ['sbatch', '-W']
    cmd_parts += [f'autodetection_{partition_name}.sh']
    cmd = ' '.join(cmd_parts)
    try:
        print("Remote autodection script submitted...")
        completed = subprocess.run(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                    universal_newlines=True, check = True, shell=True)
        return True
    except Exception as e:
        raise e
        return False


@contextmanager
def change_dir(destination : str):
    original_dir = os.getcwd()  # Save the current working directory
    try:
        os.chdir(destination)   # Change to the new directory
        yield
    finally:
        os.chdir(original_dir)  # Change back to the original directory