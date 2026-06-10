# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
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
    #                       Basic sanity checks for testing
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'SLEEP'
    check.TAGS = {'sysint-SLEEP', 'production', 'maintenance'}

    check(
        'timeout -v -k 3 3 sleep 1',
        name='timeout-completes',
        descr='Verify timeout completes successfully',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=[r'', 'stderr'],
    )
    check(
        'timeout -v -k 3 2 sleep 4',
        name='timeout-signal-term',
        descr='Verify timeout delivers TERM after expiry',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=[r'sending signal TERM', 'stderr'],
    )

    # ----------------------------------------------------------------------- #
    #
    #                                   Filesytem
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'FS'
    check.TAGS = {'sysint-FS', 'production', 'maintenance'}

    check(
        'timeout -v -k 5 3 df > /dev/null',
        name='df-command-timeout',
        descr='Verify df command completes without timeout',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=[r'sending signal',  'stderr']
    )
    check(
        'timeout -v -k 3 3 df | grep -v /dev | grep 100%',
        name='fs-no-full',
        descr='Verify filesystem is not at 100% capacity',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'',
        not_expected=[r'sending signal',  'stderr']
    )

    check(
        'findmnt -u -O nosuid /ritom/scratch || echo FAILED',
        name='ritom-mount-nosuid',
        descr='Verify ritom nosuid',
        valid_systems=['eiger', 'daint', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'findmnt -u -O remoteports=172.28.55.1-172.28.55.96 /ritom/scratch || echo FAILED',
        name='ritom-mount-remoteports',
        descr='Verify ritom remoteports=172.28.55.1-172.28.55.96',
        valid_systems=['eiger', 'daint', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'findmnt -u -O nconnect=64 /ritom/scratch || echo FAILED',
        name='ritom-mount-nconnect',
        descr='Verify ritom nconnect=64',
        valid_systems=['daint', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'findmnt -u -O optlockflush /ritom/scratch || echo FAILED',
        name='ritom-mount-optlockflush',
        descr='Verify ritom optlockflush',
        valid_systems=['eiger', 'daint', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'findmnt -u -O noextend /ritom/scratch || echo FAILED',
        name='ritom-mount-noextend',
        descr='Verify ritom noextend',
        valid_systems=['eiger', 'daint', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'findmnt -u -O lookupcache=pos /ritom/scratch || echo FAILED',
        name='ritom-mount-loopupcache',
        descr='Verify ritom lookupcache=pos',
        valid_systems=['daint', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'findmnt -u -O spread_reads /ritom/scratch || echo FAILED',
        name='ritom-mount-spread_reads',
        descr='Verify ritom spread_reads',
        valid_systems=['daint', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'findmnt -u -O spread_writes /ritom/scratch || echo FAILED',
        name='ritom-mount-spread_writes',
        descr='Verify ritom spread_writes',
        valid_systems=['daint', 'clariden'],
        not_expected=r'FAILED'
    )


    # ----------------------------------------------------------------------- #
    #
    #                                   Network
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'PING'
    check.TAGS = {'sysint-PING', 'production', 'maintenance'}

    check(
        'ping -n -q -c 5 127.0.0.1',
        name='ping-localhost',
        descr='Verify localhost ping is successful',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'5 packets transmitted, 5 received, 0% packet loss',
    )
    check(
        'ping -n -q -c 5 8.8.8.8',
        name='ping-remote-dns',
        descr='Verify remote internet ping routing via DNS',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'5 packets transmitted, 5 received, 0% packet loss',
        #where='+remote',
    )
    check(
        'ping -n -q -c 5 www.google.com',
        name='ping-remote-http',
        descr='Verify remote HTTP hostname resolves and responds to ping',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'5 packets transmitted, 5 received, 0% packet loss',
        #where='+remote',
    )

    # check('ping -n -q -c 5  8.8.8.8',        expected=r'5 packets transmitted, 5 received, 0% packet loss', where='-remote')
    # check('ping -n -q -c 5  www.google.com', expected=r'5 packets transmitted, 5 received, 0% packet loss', where='-remote')

    check.CLASS = 'PROXY'
    check.TAGS = {'sysint-PROXY', 'production', 'maintenance'}

    # check('printenv http_proxy',  expected=r'http://proxy.cscs.ch:8080', where='+remote')
    # check('printenv https_proxy', expected=r'http://proxy.cscs.ch:8080', where='+remote')
    # check('printenv no_proxy',    expected=r'.local,.cscs.ch,localhost,148.187.0.0/16,10.0.0.0/8,172.16.0.0/12', where='+remote')

    # check('printenv http_proxy', expected=r'', where='-remote')
    # check('printenv https_proxy', expected=r'', where='-remote')
    # check('printenv no_proxy', expected=r'', where='-remote')

    check(
        'curl -s www.google.com -o /dev/null || echo FAILED',
        name='curl-external-access',
        descr='Verify external internet connectivity via curl',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )

    check.CLASS = 'DNS'
    check.TAGS = {'sysint-DNS', 'production', 'maintenance'}

    check(
        'nslookup Xgit.cscs.ch    -timeout=5 || echo FAILED',
        name='dns-invalid-hostname',
        descr='Verify DNS lookup fails for invalid hostname',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'FAILED'
    )
    check(
        'nslookup  git.cscs.ch    -timeout=5 || echo FAILED',
        name='dns-internal-host',
        descr='Verify DNS resolution for internal CSCS host',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'nslookup  www.google.com -timeout=5 || echo FAILED',
        name='dns-external-host',
        descr='Verify DNS resolution for external internet host',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )

    check.CLASS = 'NETIFACE'
    check.TAGS = {'sysint-NETIFACE', 'production', 'maintenance'}

    check(
        'ip address show | grep -A6 nmn0: ',
        name='netiface-nmn0-up',
        descr='Verify nmn0 network interface is up',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'nmn0.*state UP'
    )
    check(
        'ip address show | grep -A6 nmn0: ',
        name='netiface-nmn0-ip',
        descr='Verify nmn0 has expected IP address range',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'inet 10.100.*.*/22 brd 10.100.*.255 scope global nmn0'
    )

    check(
        'ip address show | grep -A6 hsn0: ',
        name='netiface-hsn0-up',
        descr='Verify hsn0 network interface is up',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'hsn0.*state UP'
    )
    check(
        'ip address show | grep -A6 hsn0: ',
        name='netiface-hsn0-ip',
        descr='Verify hsn0 has expected IP address range',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'inet 172.28.*.*/16 * scope global hsn0'
        #expected=r'inet 172.28.*.*/16 brd 172.28.255.255 scope global hsn0'
    )

    check(
        'ip address show | grep -A6 hsn1: ',
        name='netiface-hsn1-up',
        descr='Verify hsn1 network interface is up',
        valid_systems=['daint', 'santis', 'clariden'],
        expected=r'hsn1.*state UP'
    )
    check(
        'ip address show | grep -A6 hsn1: ',
        name='netiface-hsn1-ip',
        descr='Verify hsn1 has expected IP address range',
        valid_systems=['daint', 'santis', 'clariden'],
        expected=r'inet 172.28.*.*/16 * scope global hsn1'
        #expected=r'inet 172.28.*.*/16 brd 172.28.255.255 scope global hsn1'
    )

    check(
        'ip address show | grep -A6 hsn2: ',
        name='netiface-hsn2-up',
        descr='Verify hsn2 network interface is up',
        valid_systems=['daint', 'santis', 'clariden'],
        expected=r'hsn2.*state UP'
    )
    check(
        'ip address show | grep -A6 hsn2: ',
        name='netiface-hsn2-ip',
        descr='Verify hsn2 has expected IP address range',
        valid_systems=['daint', 'santis', 'clariden'],
        expected=r'inet 172.28.*.*/16 * scope global hsn2'
        #expected=r'inet 172.28.*.*/16 brd 172.28.255.255 scope global hsn2'
    )

    check(
        'ip address show | grep -A6 hsn3: ',
        name='netiface-hsn3-up',
        descr='Verify hsn3 network interface is up',
        valid_systems=['daint', 'santis', 'clariden'],
        expected=r'hsn3.*state UP'
    )
    check(
        'ip address show | grep -A6 hsn3: ',
        name='netiface-hsn3-ip',
        descr='Verify hsn3 has expected IP address range',
        valid_systems=['daint', 'santis', 'clariden'],
        expected=r'inet 172.28.*.*/16 * scope global hsn3'
        #expected=r'inet 172.28.*.*/16 brd 172.28.255.255 scope global hsn3'
    )

    check(
        'slingshot-show-cxi-iommu-group | grep type=identity | wc -l',
        name='slingshot-iommu-group',
        descr='Verify CXI IOMMU group is set to identity on all NICs',
        valid_systems=['daint', 'santis', 'clariden'],
        expected=r'4'
    )
    check(
        'grep -q "iommu.passthrough=y"  /proc/cmdline || echo FAILED',
        name='slingshot-iommu-passthrough',
        descr='Verify IOMMU pass through is enabled on Eiger',
        valid_systems=['eiger'],
        not_expected=r'FAILED'
    )

    # ----------------------------------------------------------------------- #
    #
    #                                     LDAP
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'LDAP'
    check.TAGS = {'sysint-LDAP', 'production', 'maintenance'}

    check(
        'ping -n -q -c 5  ldap.cscs.ch',
        name='ldap-server-reachable',
        descr='Verify LDAP server is reachable',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'5 packets transmitted, 5 received, 0% packet loss'
    )
    check(
        'timeout -v -k 3 3 getent hosts',
        name='ldap-getent-hosts',
        descr='Verify getent hosts command works for LDAP',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'localhost',
        not_expected=r'sending signal'
    )

    # ----------------------------------------------------------------------- #
    #
    #                               OS installation
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'OSINSTALL'
    check.TAGS = {'sysint-OSINSTALL', 'production', 'maintenance'}

    check(
        'cat /etc/os-release',
        name='os-version-check-daint',
        descr='Verify SUSE Linux Enterprise Server 15 SP6 is installed',
        valid_systems=['daint', 'santis', 'clariden'],
        expected=r'PRETTY_NAME="SUSE Linux Enterprise Server 15 SP6"'
    )
    check(
        'cat /etc/os-release',
        name='os-version-check-eiger',
        descr='Verify SUSE Linux Enterprise Server 15 SP5 is installed (Eiger)',
        valid_systems=['eiger'],
        expected=r'PRETTY_NAME="SUSE Linux Enterprise Server 15 SP5"'
    )
    check(
        'cat /etc/locale.conf',
        name='locale-check',
        descr='Verify locale is set to en_US.UTF-8',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'LANG=en_US.UTF-8'
    )

    # ----------------------------------------------------------------------- #
    #
    #                                 OS services
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'OSSERVICE'
    check.TAGS = {'sysint-OSSERVICE', 'production', 'maintenance'}

    check(
        'ps aux | grep /usr/sbin/sshd | grep root || echo FAILED',
        name='sshd-running',
        descr='Verify SSH daemon is running',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        '/usr/bin/ss -ltup | grep :ssh  || echo FAILED',
        name='ssh-port-listening',
        descr='Verify SSH port is listening',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )

    # check('/usr/bin/ss -ltup | grep :smtp || echo FAILED', expected=r'FAILED')
    # check('/usr/bin/ss -ltup | grep :x11  || echo FAILED', expected=r'FAILED')

    check(
        '/usr/bin/ss -ltup | grep :http || echo FAILED',
        name='http-port-not-listening',
        descr='Verify HTTP port is not listening',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'FAILED'
    )

    # ----------------------------------------------------------------------- #
    #
    #                         Cray Programming Environment (deprecated)
    #
    # ----------------------------------------------------------------------- #

#    check.CLASS = "CPE"

#    check('bash -c "module --redirect load cray || echo FAILED"', not_expected=r'FAILED')
#    check('bash -c "module --redirect load cray && module --redirect list"', expected=r'craype-arm-grace', not_expected=r'craype-x86-rome')

#    check('bash -c "module --redirect spider PrgEnv-cray/8.5.0   || echo FAILED"', not_expected=r'FAILED')
#    check('bash -c "module --redirect spider PrgEnv-gnu/8.5.0    || echo FAILED"', not_expected=r'FAILED')
#    check('bash -c "module --redirect spider PrgEnv-nvidia/8.5.0 || echo FAILED"', not_expected=r'FAILED')

    # ----------------------------------------------------------------------- #
    #
    #                                Basic tools
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'TOOLS'
    check.TAGS = {'sysint-TOOLS', 'production', 'maintenance'}

    check(
        'which zypper || echo FAILED',
        name='tool-zypper',
        descr='Verify zypper package manager is available',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'which vim    || echo FAILED',
        name='tool-vim',
        descr='Verify vim editor is available',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'which gcc    || echo FAILED',
        name='tool-gcc',
        descr='Verify gcc compiler is available',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'which gcc-12 || echo FAILED',
        name='tool-gcc-12',
        descr='Verify gcc-12 compiler is available',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'which emacs || echo FAILED',
        name='tool-emacs',
        descr='Verify emacs editor is available',
        valid_systems=['eiger'],
        not_expected=r'FAILED'
    )

    # CI-Ext
    check(
        'which jq     || echo FAILED',
        name='tool-jq',
        descr='Verify jq JSON processor is available',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )

    # TODO: deploy https://github.com/eth-cscs/alps-uenv/pull/130
    # check('which emacs || echo FAILED', not_expected=r'FAILED')

    # ----------------------------------------------------------------------- #
    #
    #                               Mount-points
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'MOUNTS'
    check.TAGS = {'sysint-MOUNTS', 'production', 'maintenance'}

    check(
        'grep -q "/users/cscs /users nfs"                 /proc/mounts || echo FAILED',
        name='mount-users-eiger',
        descr='Verify /users NFS mount (Eiger)',
        valid_systems=['eiger'],
        not_expected=r'FAILED'
    )
    check(
        'grep -q "pe_opt_cray_pe /opt/cray/pe"  /proc/mounts || echo FAILED',
        name='mount-cray-pe-eiger',
        descr='Verify Cray PE mount (Eiger)',
        valid_systems=['eiger'],
        not_expected=r'FAILED'
    )
    check(
        'grep -q "pe_opt_AMD /opt/AMD"          /proc/mounts || echo FAILED',
        name='mount-amd-eiger',
        descr='Verify AMD module mount (Eiger)',
        valid_systems=['eiger'],
        not_expected=r'FAILED'
    )
    check(
        'grep -q "pe_opt_intel /opt/intel"      /proc/mounts || echo FAILED',
        name='mount-intel-eiger',
        descr='Verify Intel module mount (Eiger)',
        valid_systems=['eiger'],
        not_expected=r'FAILED'
    )
    check(
        'grep -q "/capstor/scratch/cscs /capstor/scratch/cscs lustre"     /proc/mounts || echo FAILED',
        name='mount-scratch-capstor',
        descr='Verify scratch filesystem is mounted',
        valid_systems=['daint', 'eiger', 'santis'],
        not_expected=r'FAILED'
    )
    check(
        'grep -q "/iopsstor/scratch/cscs /iopsstor/scratch/cscs lustre"     /proc/mounts || echo FAILED',
        name='mount-scratch-iopsstor',
        descr='Verify scratch filesystem is mounted (Clariden)',
        valid_systems=['clariden'],
        not_expected=r'FAILED'
    )
    check(
        'grep -q "/capstor/store/cscs /capstor/store/cscs lustre"         /proc/mounts || echo FAILED',
        name='mount-store-capstor',
        descr='Verify store filesystem is mounted (capstor)',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )

    check(
        'printenv SCRATCH || echo FAILED',
        name='env-scratch',
        descr='Verify SCRATCH environment variable is set',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'printenv PROJECT || echo FAILED',
        name='env-project',
        descr='Verify PROJECT environment variable is set',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'printenv STORE   || echo FAILED',
        name='env-store',
        descr='Verify STORE environment variable is set',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'printenv APPS    || echo FAILED',
        name='env-apps-eiger',
        descr='Verify APPS environment variable is set (Eiger)',
        valid_systems=['eiger'],
        not_expected=r'FAILED'
    )
    check(
        'printenv HOME    || echo FAILED',
        name='env-home',
        descr='Verify HOME environment variable is set',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )

    check(
        'bash -c "[[ $SCRATCH == /capstor/scratch/cscs/*  ]] || echo FAILED"',
        name='scratch-path-check-capstor',
        descr='Verify SCRATCH path is under /capstor/scratch/cscs',
        valid_systems=['daint', 'eiger', 'santis'],
        not_expected=r'FAILED'
    )
    check(
        'bash -c "[[ $SCRATCH == /iopsstor/scratch/cscs/*  ]] || echo FAILED"',
        name='scratch-path-check-iopsstor',
        descr='Verify SCRATCH path is under /iopsstor/scratch/cscs',
        valid_systems=['clariden'],
        not_expected=r'FAILED'
    )
    check(
        'bash -c "[[ $PROJECT == /capstor/store/cscs/*    ]] || echo FAILED"',
        name='project-path-check',
        descr='Verify PROJECT path is under /capstor/store/cscs',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'bash -c "[[ $STORE   == /capstor/store/cscs/*    ]] || echo FAILED"',
        name='store-path-check',
        descr='Verify STORE path is under /capstor/store/cscs',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'bash -c "[[ $APPS    == /capstor/apps/cscs/eiger ]] || echo FAILED"',
        name='apps-path-check-eiger',
        descr='Verify APPS path is /capstor/apps/cscs/eiger (Eiger)',
        valid_systems=['eiger'],
        not_expected=r'FAILED'
    )
    check(
        'bash -c "[[ $HOME    == /users/*                 ]] || echo FAILED"',
        name='home-path-check',
        descr='Verify HOME path is under /users',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )

    check(
        'printenv TMP || echo FAILED',
        name='env-tmp-not-set',
        descr='Verify TMP environment variable is not set',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'FAILED'
    )

    # ----------------------------------------------------------------------- #
    #
    #                                   Slurm
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'SLURM'
    check.TAGS = {'sysint-SLURM', 'production', 'maintenance'}

    # check('test -e /etc/slurm/slurm.conf      || echo FAILED', not_expected=r'FAILED', where='-remote')
    check(
        #'test -e /run/slurm/conf/slurm.conf || echo FAILED',
        '(test -e /run/slurm/conf/slurm.conf -o -e /etc/slurm/slurm.conf) || echo FAILED',
        name='slurm-config-exists',
        descr='Verify Slurm configuration file exists',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED',
        where='+remote',
    )

    check(
        'which sinfo || echo FAILED',
        name='slurm-sinfo-tool',
        descr='Verify Slurm sinfo tool is available',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )
    check(
        'ps aux | grep munge',
        name='slurm-munge-daemon',
        descr='Verify Munge daemon is running',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'/usr/sbin/munged'
    )
    check(
        'scontrol ping',
        name='slurm-slurmctld-ping',
        descr='Verify Slurm controller is responsive',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        expected=r'Slurmctld\(primary\) at .* is UP'
    )
    # no need of a backup on daint thanks to kubernetes
    # check('scontrol ping', expected=r'Slurmctld\(backup\) at .* is UP')
    # check('grep "JobComp" /etc/slurm/slurm.conf | grep -v "#"', expected=r'kafka', not_expected=r'elasticsearch', where='-remote')
    # check('grep "JobComp" /run/slurm/conf/slurm.conf | grep -v "#"', expected=r'kafka', not_expected=r'elasticsearch', where='+remote')

    # ----------------------------------------------------------------------- #
    #
    #                           vService fundamentals
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'VSBASE'
    check.TAGS = {'sysint-VSBASE', 'production', 'maintenance'}

    check(
        'which nomad || echo FAILED',
        name='vsbase-nomad',
        descr='Verify Nomad orchestrator is available',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )

    # ----------------------------------------------------------------------- #
    #
    #                             Expected vServices
    #
    # ----------------------------------------------------------------------- #

    check.CLASS = 'VSERVICES'
    check.TAGS = {'sysint-VSERVICES', 'production', 'maintenance'}

    check(
        'bash -c "uenv --version" || echo FAILED',
        name='vservices-uenv-version',
        descr='Verify uenv command is available and works',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED'
    )
    # https://confluence.cscs.ch/display/KB/Scientific+Applications:
    # CP2K, GROMACS, LAMMPS, NAMD, QuantumESPRESSO, VASP, Forge
    check(
        'bash -c "uenv image find"',
        name='vservices-image-cp2k',
        descr='Verify CP2K image available for GH200',
        valid_systems=['daint'],
        expected=r'cp2k/.*gh200'
    )
    check(
        'bash -c "uenv image find"',
        name='vservices-image-gromacs',
        descr='Verify GROMACS image available for GH200',
        valid_systems=['daint'],
        expected=r'gromacs/.*gh200'
    )
    check(
        'bash -c "uenv image find"',
        name='vservices-image-lammps',
        descr='Verify LAMMPS image available for GH200',
        valid_systems=['daint'],
        expected=r'lammps/.*gh200'
    )
    check(
        'bash -c "uenv image find"',
        name='vservices-image-namd',
        descr='Verify NAMD image available for GH200',
        valid_systems=['daint'],
        expected=r'namd/.*gh200'
    )
    check(
        'bash -c "uenv image find"',
        name='vservices-image-quantumespresso',
        descr='Verify QuantumESPRESSO image available for GH200',
        valid_systems=['daint', 'santis'],
        expected=r'quantumespresso/.*gh200'
    )
    check(
        'bash -c "uenv image find"',
        name='vservices-image-vasp',
        descr='Verify VASP image available for GH200',
        valid_systems=['daint'],
        expected=r'vasp/.*gh200'
    )
    check(
        'bash -c "uenv image find"',
        name='vservices-image-linaro-forge',
        descr='Verify Linaro Forge image available for GH200',
        valid_systems=['daint', 'santis', 'clariden'],
        expected=r'linaro-forge/.*gh200'
    )

    check(
        'bash -c "uenv image find"',
        name='vservices-image-pytorch',
        descr='Verify PyTorch image available for GH200',
        valid_systems=['daint', 'santis', 'clariden'],
        expected=r'pytorch/.*gh200'
    )
    check(
        'bash -c "uenv image find"',
        name='vservices-image-icon-wcp-not-available',
        descr='Verify ICON-WCP image is not available for GH200',
        valid_systems=['daint', 'clariden'],
        not_expected=r'icon-wcp/.*gh200'
    )
    check(
        'bash -c "uenv image find"',
        name='vservices-image-prgenv-nvidia-not-available',
        descr='Verify PrgEnv-nvidia image is not available for GH200',
        valid_systems=['daint', 'santis', 'clariden'],
        not_expected=r'prgenv-nvidia/.*gh200'
    )

    check(
        'bash -c "uenv image find"',
        name='vservices-image-prgenv-gnu',
        descr='Verify PrgEnv-gnu image available for GH200',
        valid_systems=['daint', 'santis', 'clariden'],
        expected=r'prgenv-gnu/.*gh200'
    )
    check(
        'bash -c "uenv image find"',
        name='vservices-image-netcdf-tools',
        descr='Verify NetCDF tools image available for GH200',
        valid_systems=['daint', 'santis', 'clariden'],
        expected=r'netcdf-tools/.*gh200'
    )
    check(
        'bash -c "uenv image find"',
        name='vservices-image-editors',
        descr='Verify editors image available for GH200',
        valid_systems=['daint', 'santis', 'clariden'],
        expected=r'editors/.*gh200'
    )

    # ----------------------------------------------------------------------- #
    #
    #                               Libraries
    #
    # ----------------------------------------------------------------------- #

    check(
        'test -e /opt/cray/libfabric/ || echo FAILED',
        name='libfabric-installed',
        descr='Verify system libfabric directory is available',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED',
    )
    check(
        'test -e /opt/cray/libfabric/1.22.0/ || echo FAILED',
        name='libfabric-1_22_0-installed',
        descr='Verify system libfabric v1.22.0 is available',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED',
    )
    check(
        'test -e /opt/cray/libfabric/host/ || echo FAILED',
        name='libfabric-host-directory',
        descr='Verify system libfabric host directory is present',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED',
    )

    # ----------------------------------------------------------------------- #
    #
    #                               Workarounds
    #
    # ----------------------------------------------------------------------- #

    check(
        'test -e /capstor/store/cscs/cscs/public/temp/cuptrgetattr_override.so || echo FAILED',
        name='workaround-cupointers',
        descr='Verify cuPointerGetAttribute[s] workaround library is present',
        valid_systems=['daint', 'eiger', 'santis', 'clariden'],
        not_expected=r'FAILED',
    )

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
    import reframe as rfm  # noqa: F401

    check.MODULE_NAME = __name__

create_checks(check)
