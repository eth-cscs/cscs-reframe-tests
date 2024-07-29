# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

# --------------------------------------------------------------------------- #
#                         S T A R T   O F   C H E C K S                       #
# --------------------------------------------------------------------------- #

def create_checks(check):

#-----------------------------------------------------------------------------#
#                                                                             #
#                   These checks are only intended for Eiger                  #
#                                                                             #
#-----------------------------------------------------------------------------#

    check.SYSTEM = 'todi'

#-----------------------------------------------------------------------------#
#                                                                             #
#                       Basic sanity checks for testing                       #
#                                                                             #
#-----------------------------------------------------------------------------#

    check.CLASS = 'SLEEP'

    check('timeout -v -k 3 3 sleep 1', expected=['',                    'stderr'])
    check('timeout -v -k 3 2 sleep 4', expected=['sending signal TERM', 'stderr'])

#-----------------------------------------------------------------------------#
#                                                                             #
#                                   Filesytem                                 #
#                                                                             #
#-----------------------------------------------------------------------------#

    check.CLASS = 'FS'

    check('timeout -v -k 5 3 df > /dev/null',                   not_expected=['sending signal',  'stderr'])
    check('timeout -v -k 3 3 df | grep -v /dev | grep 100%',    expected='', not_expected=['sending signal',  'stderr'])

#-----------------------------------------------------------------------------#
#                                                                             #
#                                   Network                                   #
#                                                                             #
#-----------------------------------------------------------------------------#

    check.CLASS = 'PING'

    check('ping -n -q -c 5  127.0.0.1',      expected='5 packets transmitted, 5 received, 0% packet loss')
    check('ping -n -q -c 5  8.8.8.8',        expected='5 packets transmitted, 0 received, 100% packet loss', where='+remote')
    check('ping -n -q -c 5  www.google.com', expected='5 packets transmitted, 0 received, 100% packet loss', where='+remote')

    check('ping -n -q -c 5  8.8.8.8',        expected='5 packets transmitted, 5 received, 0% packet loss', where='-remote')
    check('ping -n -q -c 5  www.google.com', expected='5 packets transmitted, 5 received, 0% packet loss', where='-remote')

    check.CLASS = 'PROXY'

    check('printenv http_proxy',  expected='http://proxy.cscs.ch:8080',  where='+remote')
    check('printenv https_proxy', expected='http://proxy.cscs.ch:8080', where='+remote')
    check('printenv no_proxy',    expected='.local,.cscs.ch,localhost,148.187.0.0/16,10.0.0.0/8,172.16.0.0/12', where='+remote')

    check('printenv http_proxy',  expected='', where='-remote')
    check('printenv https_proxy', expected='', where='-remote')
    check('printenv no_proxy',    expected='', where='-remote')

    check('curl -s www.google.com -o /dev/null || echo FAILED', not_expected='FAILED')

    check.CLASS = 'DNS'

    check('nslookup Xgit.cscs.ch    -timeout=5 || echo FAILED', expected='FAILED')
    check('nslookup  git.cscs.ch    -timeout=5 || echo FAILED', not_expected='FAILED')
    check('nslookup  www.google.com -timeout=5 || echo FAILED', not_expected='FAILED')

    check.CLASS = 'NETIFACE'

    check('ip address show | grep -A6 nmn0: ', expected='nmn0.*state UP')
    check('ip address show | grep -A6 nmn0: ', expected='inet 10.100.*.*/22 brd 10.100.*.255 scope global nmn0')

    check('ip address show | grep -A6 hsn0: ', expected='hsn0.*state UP')
    check('ip address show | grep -A6 hsn0: ', expected='inet 172.28.*.*/16 brd 172.28.255.255 scope global hsn0')

    check('ip address show | grep -A6 hsn1: ', expected='hsn1.*state UP')
    check('ip address show | grep -A6 hsn1: ', expected='inet 172.28.*.*/16 brd 172.28.255.255 scope global hsn1')

    check('ip address show | grep -A6 hsn2: ', expected='hsn2.*state UP')
    check('ip address show | grep -A6 hsn2: ', expected='inet 172.28.*.*/16 brd 172.28.255.255 scope global hsn2')

    check('ip address show | grep -A6 hsn3: ', expected='hsn3.*state UP')
    check('ip address show | grep -A6 hsn3: ', expected='inet 172.28.*.*/16 brd 172.28.255.255 scope global hsn3')


#-----------------------------------------------------------------------------#
#                                                                             #
#                                     LDAP                                    #
#                                                                             #
#-----------------------------------------------------------------------------#

    check.CLASS = 'LDAP'

    check('ping -n -q -c 5  ldap.cscs.ch',  expected='5 packets transmitted, 5 received, 0% packet loss')
    check('timeout -v -k 3 3 getent hosts', expected='localhost', not_expected='sending signal')

#-----------------------------------------------------------------------------#
#                                                                             #
#                               OS installation                               #
#                                                                             #
#-----------------------------------------------------------------------------#

    check.CLASS = 'OSINSTALL'

    check('cat /etc/os-release', expected='PRETTY_NAME="SUSE Linux Enterprise Server 15 SP5"')
    check('locale', expected='LANG=C')

#-----------------------------------------------------------------------------#
#                                                                             #
#                                 OS services                                 #
#                                                                             #
#-----------------------------------------------------------------------------#

    check.CLASS = 'OSSERVICE'

    check('ps aux | grep /usr/sbin/sshd | grep root || echo FAILED', not_expected='FAILED')
    check('ss -ltup | grep :ssh  || echo FAILED', not_expected='FAILED')

    check('ss -ltup | grep :smtp || echo FAILED', expected='FAILED')
    check('ss -ltup | grep :x11  || echo FAILED', expected='FAILED')

    check('ss -ltup | grep :http || echo FAILED', expected='FAILED')

#-----------------------------------------------------------------------------#
#                                                                             #
#                         Cray Programming Environment                        #
#                                                                             #
#-----------------------------------------------------------------------------#

    check.CLASS = "CPE"

    check('bash -c "module load cray || echo FAILED"', not_expected='FAILED')
    check('bash -c "module load cray && module list"', expected='craype-arm-grace', not_expected='craype-x86-rome')

    check('bash -c "module spider PrgEnv-cray/8.5.0   || echo FAILED"', not_expected='FAILED')
    check('bash -c "module spider PrgEnv-gnu/8.5.0    || echo FAILED"', not_expected='FAILED')
    check('bash -c "module spider PrgEnv-nvidia/8.5.0 || echo FAILED"', not_expected='FAILED')

#-----------------------------------------------------------------------------#
#                                                                             #
#                                Basic tools                                  #
#                                                                             #
#-----------------------------------------------------------------------------#

    check.CLASS = 'TOOLS'

    check('which zypper || echo FAILED', not_expected='FAILED')
    check('which vim    || echo FAILED', not_expected='FAILED')
    check('which gcc    || echo FAILED', not_expected='FAILED')
    check('which gcc-12 || echo FAILED', not_expected='FAILED')

#-----------------------------------------------------------------------------#
#                                                                             #
#                               Mount-points                                  #
#                                                                             #
#-----------------------------------------------------------------------------#

    check.CLASS = 'MOUNTS'

    check('grep -q "/capstor/scratch/cscs /capstor/scratch/cscs lustre"     /proc/mounts || echo FAILED', not_expected='FAILED')
    check('grep -q "/capstor/users/cscs /users lustre"                      /proc/mounts || echo FAILED', not_expected='FAILED')
    check('grep -q "/iopsstor/scratch/cscs /iopsstor/scratch/cscs lustre"   /proc/mounts || echo FAILED', not_expected='FAILED')

    check('grep -q "pe_opt_cray_pe /opt/cray/pe"  /proc/mounts || echo FAILED', not_expected='FAILED')

    check('printenv SCRATCH || echo FAILED', not_expected='FAILED')
    check('printenv PROJECT || echo FAILED', not_expected='FAILED')
    check('printenv STORE   || echo FAILED', not_expected='FAILED')
    check('printenv APPS    || echo FAILED', not_expected='FAILED')
    check('printenv HOME    || echo FAILED', not_expected='FAILED')

    check('bash -c "[[ $SCRATCH == /capstor/scratch/cscs/* ]] || echo FAILED"', not_expected='FAILED')
    check('bash -c "[[ $PROJECT == /project/*              ]] || echo FAILED"', not_expected='FAILED')
    check('bash -c "[[ $STORE   == /store/*                ]] || echo FAILED"', not_expected='FAILED')
    check('bash -c "[[ $APPS    == /capstor/apps/cscs      ]] || echo FAILED"', not_expected='FAILED')
    check('bash -c "[[ $HOME    == /users/*                ]] || echo FAILED"', not_expected='FAILED')

    check('printenv TMP || echo FAILED', expected='FAILED')

#-----------------------------------------------------------------------------#
#                                                                             #
#                                   Slurm                                     #
#                                                                             #
#-----------------------------------------------------------------------------#

    check.CLASS = 'SLURM'

    check('test -e /etc/slurm/slurm.conf || echo FAILED', not_expected='FAILED')
    check('which sinfo || echo FAILED', not_expected='FAILED')
    check('ps aux | grep munge', expected='/usr/sbin/munged')
    check('scontrol ping', expected='Slurmctld\(primary\) at .* is UP')
    check('scontrol ping', expected='Slurmctld\(backup\) at .* is UP')

#-----------------------------------------------------------------------------#
#                                                                             #
#                           vService fundamentals                             #
#                                                                             #
#-----------------------------------------------------------------------------#

    check.CLASS = 'VSBASE'

    check('which nomad || echo FAILED', not_expected='FAILED')

#-----------------------------------------------------------------------------#
#                                                                             #
#                             Expected vServices                              #
#                                                                             #
#-----------------------------------------------------------------------------#

    check.CLASS = 'VSERVICES'

    check('bash -c "uenv --version" || echo FAILED', not_expected='FAILED')
    check('bash -c "uenv image find || echo FAILED"', expected=           'vasp/.*gh200',   not_expected='FAILED');
    check('bash -c "uenv image find || echo FAILED"', expected='quantumespresso/.*gh200',   not_expected='FAILED');
    check('bash -c "uenv image find || echo FAILED"', expected=        'pytorch/.*gh200',   not_expected='FAILED');
    check('bash -c "uenv image find || echo FAILED"', expected=  'prgenv-nvidia/.*gh200',   not_expected='FAILED');
    check('bash -c "uenv image find || echo FAILED"', expected=     'prgenv-gnu/.*gh200',   not_expected='FAILED');
    check('bash -c "uenv image find || echo FAILED"', expected=   'netcdf-tools/.*gh200',   not_expected='FAILED');
    check('bash -c "uenv image find || echo FAILED"', expected=           'namd/.*gh200',   not_expected='FAILED');
    check('bash -c "uenv image find || echo FAILED"', expected=         'lammps/.*gh200',   not_expected='FAILED');
    check('bash -c "uenv image find || echo FAILED"', expected=       'icon-wcp/.*gh200',   not_expected='FAILED');
    check('bash -c "uenv image find || echo FAILED"', expected=        'gromacs/.*gh200',   not_expected='FAILED');
    check('bash -c "uenv image find || echo FAILED"', expected=        'editors/.*gh200',   not_expected='FAILED');
    check('bash -c "uenv image find || echo FAILED"', expected=           'cp2k/.*gh200',   not_expected='FAILED');
    check('bash -c "uenv image find || echo FAILED"', expected=          'arbor/.*gh200',   not_expected='FAILED');



# --------------------------------------------------------------------------- #
#                           E N D   O F   C H E C K S                         #
# --------------------------------------------------------------------------- #




# --------------------------------------------------------------------------- # 
#                          S T A R T   U P   C O D E                          #
# --------------------------------------------------------------------------- #


from utils import Check 

check = Check()

if __name__ == '__main__':
    check.DEBUG = True
else:
    import reframe as rfm
    check.MODULE_NAME = __name__

create_checks(check)
