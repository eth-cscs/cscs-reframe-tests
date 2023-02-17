import os
import logging
import itertools
import subprocess

_SARUS_DEVICEQUERY_COMMAND = (
    'sarus run ethcscs/cudasamples:8.0 /usr/local/cuda/samples/1_Utilities/'
    'deviceQuery/deviceQuery')

_NATIVE_DEVICEQUERY_COMMAND = (
    '/cm/shared/apps/easybuild/software/CUDA/7.5.18/samples/bin/x86_64/linux/'
    'release/deviceQuery')


def get_devicequery_output(command):
    process = subprocess.run(command, stdout=subprocess.PIPE,
                             universal_newlines=True)
    try:
        process.check_returncode()
    except subprocess.CalledProcessError:
        raise
    logging.debug(process.stdout)
    return process.stdout.splitlines()


def get_device_pci_ids(devicequery_output):
    ids = []
    for line in devicequery_output:
        if 'Device PCI Domain ID' in line:
            ids.append(line.split(':')[1].strip())
    return ids


def get_device_names(devicequery_output):
    summary = [s.strip() for s in devicequery_output[-2].split(',')]
    names = []
    for line in summary:
        if 'Device' in line:
            names.append(line.split(' = ')[1])
    return names


def generate_gpu_ids_permutations(gpu_ids):
    for permutation_length in range(1, len(gpu_ids)+1):
        for permutation in itertools.permutations(gpu_ids, permutation_length):
            yield permutation


def run_check():
    gpu_ids = [int(i) for i in os.environ['CUDA_VISIBLE_DEVICES'].split(',')]
    output = get_devicequery_output(_NATIVE_DEVICEQUERY_COMMAND)
    native_pci_ids = get_device_pci_ids(output)
    native_device_names = get_device_names(output)
    for permutation in generate_gpu_ids_permutations(gpu_ids):
        print(f'Testing permutation {permutation}')
        os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(
            [str(n) for n in permutation])
        output = get_devicequery_output(_SARUS_DEVICEQUERY_COMMAND)
        sarus_pci_ids = get_device_pci_ids(output)
        sarus_device_names = get_device_names(output)

        expected_device_names = [native_device_names[i] for i in permutation]
        names_assert_msg = (f'found sarus devices: {sarus_device_names}, '
                            f'but expected {expected_device_names}')

        assert sarus_device_names == expected_device_names, names_assert_msg

        expected_pci_ids = [native_pci_ids[i] for i in permutation]
        ids_assert_msg = (
            f'found sarus pci ids: {sarus_pci_ids}, but expected '
            f'{expected_pci_ids}')

        assert sarus_pci_ids == expected_pci_ids, ids_assert_msg


if __name__ == '__main__':
    try:
        run_check()
    except Exception as e:
        logging.error('check failed')
        logging.error('exception: ' + str(e))
    else:
        print('CHECK SUCCESSFUL')
