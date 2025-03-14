# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

from utils import Check


# --------------------------------------------------------------------------- #
#                         S T A R T   O F   C H E C K S
# --------------------------------------------------------------------------- #


def create_checks(check):

    # ----------------------------------------------------------------------- #
    #
    #                   These checks are only intended for Alps-Daint
    #
    # ----------------------------------------------------------------------- #

    check.SYSTEM = 'daint'

    # ----------------------------------------------------------------------- #
    #
    #                       Basic sanity checks for testing
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'SLEEP'

    check('timeout -v -k 3 3 sleep 1', expected=[r'', 'stderr'])
    check('timeout -v -k 3 2 sleep 4', expected=[r'sending signal TERM', 'stderr'])

    # ----------------------------------------------------------------------- #
    #
    #                                   Filesytem
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'FS'

    check('timeout -v -k 5 3 df > /dev/null',                not_expected=[r'sending signal',  'stderr'])
    check('timeout -v -k 3 3 df | grep -v /dev | grep 100%', expected=r'', not_expected=[r'sending signal',  'stderr'])

    # ----------------------------------------------------------------------- #
    #
    #                                   Network
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'PING'

    check('ping -n -q -c 5  127.0.0.1',      expected=r'5 packets transmitted, 5 received, 0% packet loss')
    check('ping -n -q -c 5  8.8.8.8',        expected=r'5 packets transmitted, 0 received, 100% packet loss', where='+remote')
    check('ping -n -q -c 5  www.google.com', expected=r'5 packets transmitted, 0 received, 100% packet loss', where='+remote')

    # check('ping -n -q -c 5  8.8.8.8',        expected=r'5 packets transmitted, 5 received, 0% packet loss', where='-remote')
    # check('ping -n -q -c 5  www.google.com', expected=r'5 packets transmitted, 5 received, 0% packet loss', where='-remote')

    check.CLASS = 'PROXY'

    check('printenv http_proxy',  expected=r'http://proxy.cscs.ch:8080', where='+remote')
    check('printenv https_proxy', expected=r'http://proxy.cscs.ch:8080', where='+remote')
    check('printenv no_proxy',    expected=r'.local,.cscs.ch,localhost,148.187.0.0/16,10.0.0.0/8,172.16.0.0/12', where='+remote')

    # check('printenv http_proxy', expected=r'', where='-remote')
    # check('printenv https_proxy', expected=r'', where='-remote')
    # check('printenv no_proxy', expected=r'', where='-remote')

    check('curl -s www.google.com -o /dev/null || echo FAILED', not_expected=r'FAILED')

    check.CLASS = 'DNS'

    check('nslookup Xgit.cscs.ch    -timeout=5 || echo FAILED', expected=r'FAILED')
    check('nslookup  git.cscs.ch    -timeout=5 || echo FAILED', not_expected=r'FAILED')
    check('nslookup  www.google.com -timeout=5 || echo FAILED', not_expected=r'FAILED')

    check.CLASS = 'NETIFACE'

    check('ip address show | grep -A6 nmn0: ', expected=r'nmn0.*state UP')
    check('ip address show | grep -A6 nmn0: ', expected=r'inet 10.100.*.*/22 brd 10.100.*.255 scope global nmn0')

    check('ip address show | grep -A6 hsn0: ', expected=r'hsn0.*state UP')
    check('ip address show | grep -A6 hsn0: ', expected=r'inet 172.28.*.*/16 brd 172.28.255.255 scope global hsn0')

    check('ip address show | grep -A6 hsn1: ', expected=r'hsn1.*state UP')
    check('ip address show | grep -A6 hsn1: ', expected=r'inet 172.28.*.*/16 brd 172.28.255.255 scope global hsn1')

    check('ip address show | grep -A6 hsn2: ', expected=r'hsn2.*state UP')
    check('ip address show | grep -A6 hsn2: ', expected=r'inet 172.28.*.*/16 brd 172.28.255.255 scope global hsn2')

    check('ip address show | grep -A6 hsn3: ', expected=r'hsn3.*state UP')
    check('ip address show | grep -A6 hsn3: ', expected=r'inet 172.28.*.*/16 brd 172.28.255.255 scope global hsn3')

    # ----------------------------------------------------------------------- #
    #
    #                                     LDAP
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'LDAP'

    check('ping -n -q -c 5  ldap.cscs.ch', expected=r'5 packets transmitted, 5 received, 0% packet loss')
    check('timeout -v -k 3 3 getent hosts', expected=r'localhost', not_expected=r'sending signal')

    # ----------------------------------------------------------------------- #
    #
    #                               OS installation
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'OSINSTALL'

    check('cat /etc/os-release', expected=r'PRETTY_NAME="SUSE Linux Enterprise Server 15 SP5"')
    check('cat /etc/locale.conf', expected=r'LANG=en_US.UTF-8')

    # ----------------------------------------------------------------------- #
    #
    #                                 OS services
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'OSSERVICE'

    check('ps aux | grep /usr/sbin/sshd | grep root || echo FAILED', not_expected=r'FAILED')
    check('/usr/bin/ss -ltup | grep :ssh  || echo FAILED', not_expected=r'FAILED')

    # check('/usr/bin/ss -ltup | grep :smtp || echo FAILED', expected=r'FAILED')
    # check('/usr/bin/ss -ltup | grep :x11  || echo FAILED', expected=r'FAILED')

    check('/usr/bin/ss -ltup | grep :http || echo FAILED', expected=r'FAILED')

    # ----------------------------------------------------------------------- #
    #
    #                         Cray Programming Environment
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = "CPE"

    check('bash -c "module --redirect load cray || echo FAILED"', not_expected=r'FAILED')
    check('bash -c "module --redirect load cray && module --redirect list"', expected=r'craype-arm-grace', not_expected=r'craype-x86-rome')

    check('bash -c "module --redirect spider PrgEnv-cray/8.5.0   || echo FAILED"', not_expected=r'FAILED')
    check('bash -c "module --redirect spider PrgEnv-gnu/8.5.0    || echo FAILED"', not_expected=r'FAILED')
    check('bash -c "module --redirect spider PrgEnv-nvidia/8.5.0 || echo FAILED"', not_expected=r'FAILED')

    # ----------------------------------------------------------------------- #
    #
    #                                Basic tools
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'TOOLS'

    check('which zypper || echo FAILED', not_expected=r'FAILED')
    check('which vim    || echo FAILED', not_expected=r'FAILED')
    check('which gcc    || echo FAILED', not_expected=r'FAILED')
    check('which gcc-12 || echo FAILED', not_expected=r'FAILED')

    # CI-Ext
    check('which jq     || echo FAILED', not_expected=r'FAILED')

    # TODO: deploy https://github.com/eth-cscs/alps-uenv/pull/130
    # check('which emacs || echo FAILED', not_expected=r'FAILED')

    # ----------------------------------------------------------------------- #
    #
    #                               Mount-points
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'MOUNTS'

    check('grep -q "/capstor/scratch/cscs /capstor/scratch/cscs lustre"     /proc/mounts || echo FAILED', not_expected=r'FAILED')
    check('grep -q "/capstor/store/cscs /capstor/store/cscs lustre"         /proc/mounts || echo FAILED', not_expected=r'FAILED')
    check('grep -q "/capstor/users/cscs /users.OLD lustre"                  /proc/mounts || echo FAILED', not_expected=r'FAILED')
    check('grep -q "/capstor/store/cscs /store lustre"                      /proc/mounts || echo FAILED', not_expected=r'FAILED')

    check('grep -q "pe_opt_cray_pe /opt/cray/pe"  /proc/mounts || echo FAILED', not_expected=r'FAILED')

    check('printenv SCRATCH || echo FAILED', not_expected=r'FAILED')
    check('printenv PROJECT || echo FAILED', not_expected=r'FAILED')
    check('printenv STORE   || echo FAILED', not_expected=r'FAILED')
    # check('printenv APPS    || echo FAILED', not_expected=r'FAILED')
    check('printenv HOME    || echo FAILED', not_expected=r'FAILED')

    check('bash -c "[[ $SCRATCH == /capstor/scratch/cscs/*  ]] || echo FAILED"', not_expected=r'FAILED')
    check('bash -c "[[ $PROJECT == /capstor/store/cscs/*    ]] || echo FAILED"', not_expected=r'FAILED')
    check('bash -c "[[ $STORE   == /capstor/store/cscs/*    ]] || echo FAILED"', not_expected=r'FAILED')
    # check('bash -c "[[ $APPS    == /capstor/apps/cscs/daint ]] || echo FAILED"', not_expected=r'FAILED')
    check('bash -c "[[ $HOME    == /users/*                 ]] || echo FAILED"', not_expected=r'FAILED')

    check('printenv TMP || echo FAILED', expected=r'FAILED')

    # ----------------------------------------------------------------------- #
    #
    #                                   Slurm
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'SLURM'

    # check('test -e /etc/slurm/slurm.conf      || echo FAILED', not_expected=r'FAILED', where='-remote')
    check('test -e /run/slurm/conf/slurm.conf || echo FAILED', not_expected=r'FAILED', where='+remote')

    check('which sinfo || echo FAILED', not_expected=r'FAILED')
    check('ps aux | grep munge', expected=r'/usr/sbin/munged')
    check('scontrol ping', expected=r'Slurmctld\(primary\) at .* is UP')
    # no need of a backup on daint thanks to kubernetes
    # check('scontrol ping', expected=r'Slurmctld\(backup\) at .* is UP')
    # check('grep "JobComp" /etc/slurm/slurm.conf | grep -v "#"', expected=r'kafka', not_expected=r'elasticsearch', where='-remote')
    check('grep "JobComp" /run/slurm/conf/slurm.conf | grep -v "#"', expected=r'kafka', not_expected=r'elasticsearch', where='+remote')

    # ----------------------------------------------------------------------- #
    #
    #                           vService fundamentals
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'VSBASE'

    check('which nomad || echo FAILED', not_expected=r'FAILED')

    # ----------------------------------------------------------------------- #
    #
    #                             Expected vServices
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'VSERVICES'

    check('bash -c "uenv --version" || echo FAILED', not_expected=r'FAILED')
    # https://confluence.cscs.ch/display/KB/Scientific+Applications:
    # CP2K, GROMACS, LAMMPS, NAMD, QuantumESPRESSO, VASP, Forge
    check('bash -c "uenv image find"', expected=           r'cp2k/.*gh200')
    check('bash -c "uenv image find"', expected=        r'gromacs/.*gh200')
    check('bash -c "uenv image find"', expected=         r'lammps/.*gh200')
    check('bash -c "uenv image find"', expected=           r'namd/.*gh200')
    check('bash -c "uenv image find"', expected=r'quantumespresso/.*gh200')
    check('bash -c "uenv image find"', expected=           r'vasp/.*gh200')
    check('bash -c "uenv image find"', expected=   r'linaro-forge/.*gh200')

    check('bash -c "uenv image find"', not_expected=    r'pytorch/.*gh200')
    check('bash -c "uenv image find"', not_expected=   r'icon-wcp/.*gh200')
    check('bash -c "uenv image find"', not_expected=  r'prgenv-nvidia/.*gh200')

    check('bash -c "uenv image find"', expected=     r'prgenv-gnu/.*gh200')
    check('bash -c "uenv image find"', expected=   r'netcdf-tools/.*gh200')
    check('bash -c "uenv image find"', expected=        r'editors/.*gh200')


# --------------------------------------------------------------------------- #
#                           E N D   O F   C H E C K S
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
#                          S T A R T   U P   C O D E
# --------------------------------------------------------------------------- #


check = Check()

if __name__ == '__main__':
    check.DEBUG = True
else:
    import reframe as rfm

    check.MODULE_NAME = __name__

create_checks(check)
