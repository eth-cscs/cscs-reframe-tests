# Written by Jean M Favre, CSCS
# /users/jfavre/Projects/ParaView/Python/pvParaView-ConnectToCrays.py
# Test passed Mon 23 Jun 12:08:53 CEST 2025
#
# example:
# pvbatch -- pvParaViewConnectToCrays.py \
#         -p normal --host=eiger --version=5.13.2:v2
##############################################################################
from paraview.simple import *
from paraview.modules.vtkRemotingViews import vtkPVOpenGLInformation

import os
import random
import subprocess
import argparse

parser = argparse.ArgumentParser(
        description="Remote Connection tester for CSCS ALPS Vclusters")

helpstr = 'hostname to connect to: clariden, daint, santis, eiger'
parser.add_argument('--host', type=str, default='daint', help=helpstr)

parser.add_argument("--version", type=str, default='5.13.2:v2',
                    help="ParaView version: 5.13.2:v2, 6.0???")

parser.add_argument("--script", type=str,
                    default='/users/jfavre/rc-submit.alps-pvserver.sh',
                    help="remote shell script to create SLURM job")

parser.add_argument("--nodes", type=int, default=1, help="SLURM userid")

parser.add_argument("--ntasks", type=int, default=4,
                    help="SLURM ntasks: will be divided equally amongst nodes")

parser.add_argument("-userid", type=int, default=random.randint(2049, 9999),
                    help="ssh port number")

parser.add_argument("-username", type=str, default='jfavre',
                    help="ssh username for ela.cscs.ch")

parser.add_argument("--account", type=str, default='csstaff',
                    help="SLURM projectid")

parser.add_argument("-p", type=str, default='normal',
                    help="SLURM partition: debug, or normal")

parser.add_argument("--reservation", type=str, default='',
                    help="SLURM reservation: TBD")


def ParaView_Pipeline():
    renderView1 = GetRenderView()
    print('################ Local desktop ############')
    # client-side graphics hardware
    info = GetOpenGLInformation()
    print("Vendor:   %s" % info.GetVendor())
    print("Version:  %s" % info.GetVersion())
    print("Renderer: %s" % info.GetRenderer())
    print('################ Remote Render Server ############')
    # server-side graphics hardware
    info = \
        GetOpenGLInformation(location=servermanager.vtkSMSession.RENDER_SERVER)
    print("Vendor:   %s" % info.GetVendor())
    print("Version:  %s" % info.GetVersion())
    print("Renderer: %s" % info.GetRenderer())
    print('##################################################')


def main(args):
    atime = "00:09:59"   # allocation time
    memory = "standard"  # choices are "standard", or "high"
    # first the options to create ssh tunnel
    cmd = (
        f"ssh -l {args.username} -R {args.userid}:localhost:{args.userid} "
        f"{args.host} {args.script} pvserver@{args.host} {atime} {args.nodes} "
        f"{args.ntasks // args.nodes} {args.userid} {args.host} "
        f"{args.version} {args.p} {memory} {args.account} "
        f"{args.reservation}; sleep 600"
    )
    print(f"# cmd={cmd}")
    c = subprocess.Popen(cmd.split())
    ReverseConnect(str(args.userid))  # blocks until compute node calls back
    # do something graphical
    ParaView_Pipeline()


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
