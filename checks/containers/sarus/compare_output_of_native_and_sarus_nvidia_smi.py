import logging
import subprocess


_SARUS_NVIDIA_SMI_COMMAND = 'sarus run ethcscs/cudasamples:8.0 nvidia-smi -L'
_NATIVE_NVIDIA_SMI_COMMAND = '/usr/bin/nvidia-smi -L'


def get_command_output(command):
    process = subprocess.run(command, stdout=subprocess.PIPE,
                             universal_newlines=True)
    try:
        process.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'command {command} returned a non-zero exit status!')
        raise

    logging.debug(process.stdout)
    return process.stdout.splitlines()


def check_that_native_device_ids_are_equal_to_sarus_device_ids():
    native_output = get_command_output(_NATIVE_NVIDIA_SMI_COMMAND)
    sarus_output = get_command_output(_SARUS_NVIDIA_SMI_COMMAND)
    assertion_message = (
        f'Got different output between''native nvidia-smi and '
        f'Sarus nvidia-smi.\n'
        f'native output: {native_output}\n'
        f'sarus output: {sarus_output}\n')
    assert native_output == sarus_output, assertion_message


if __name__ == '__main__':
    try:
        check_that_native_device_ids_are_equal_to_sarus_device_ids()
    except Exception as e:
        logger.error('check failed. Got expection: {e}')
    else:
        print('CHECK SUCCESSFUL')
