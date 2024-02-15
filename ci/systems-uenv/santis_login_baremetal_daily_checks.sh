#!/bin/bash -x

CHECKS="\
-c config/cscs.py
-c checks/prgenv/cuda_nvml.py
-c checks/prgenv/cuda_fortran.py
-c checks/prgenv/mpi.py
-c checks/prgenv/openacc.py
-c checks/prgenv/helloworld.py
-c checks/libraries/io/hdf5.py
-c checks/libraries/io/netcdf.py
-c checks/libraries/io/pnetcdf.py
-c checks/microbenchmarks/cpu/alloc_speed/alloc_speed.py 
"

datetime () { date +"%Y-%m-%d %H:%M:%S"; }

red ()    { echo "\e[1;31m$1\e[m"; }
yellow () { echo "\e[1;33m$1\e[m"; }
log ()    { printf "$(yellow "[log $(datetime)]") $1\n"; }
err ()    { printf "$(red "[error $(datetime)]") $1\n"; exit 1; }
exit_without_error () { printf "$(yellow "[log $(datetime)]") $1\n"; exit 0; }

usage () {
    echo "usage: reframe-run -n name -s system -m mount"
    echo ""
    echo "where:"
    echo "  name:        the name of the stack"
    echo "  uarch:       microarchitecture \(one of a100, zen2, zen3, mi200\)"
    echo "  system:      the cluster name \(e.g. of balfrin, clariden, eiger\)"
    echo "  mount:       the mount point of the image"
    echo ""
    [[ "" == "$1" ]] && exit 0
    err "$1"
}

system=${STACK_SYSTEM}
name=${STACK_NAME}
uarch=${STACK_UARCH}
mount=${STACK_MOUNT}

ci_path="$CI_PROJECT_DIR"
test_path="$ci_path/$CI_JOB_ID"

[[ -z "${system}"      ]] && usage "missing system argument"
[[ -z "${name}"        ]] && usage "missing name argument"
[[ -z "${uarch}"       ]] && usage "missing uarch argument"
[[ -z "${mount}"       ]] && usage "missing mount argument"
[[ -z "${REPORT}"      ]] && usage "missing REPORT variable"

build_id=${CI_PIPELINE_ID}

log "SCRATCH     ${SCRATCH}"
log "USER        ${USER}"
log "name        ${name}"
log "system      ${system}"
log "uarch       ${uarch}"
log "mount       ${mount}"
log "build_id    ${build_id}"
log "ci_path     ${ci_path}"
log "test_path   ${test_path}"
log "slurm part. ${SLURM_PARTITION}"

log "set up a python venv and pip install reframe"
[[ -z "${SLURM_PARTITION}" ]] && RFM_SYSTEM="${system}" || RFM_SYSTEM="${system}:${SLURM_PARTITION}"

#
# Setup python environment
#

rm -rf rfm_venv
python3 -m venv rfm_venv
source rfm_venv/bin/activate

#
# Install ReFrame
#

git clone ${RFM_GIT}

(cd reframe && git checkout ${RFM_GIT_TAG} && ./bootstrap.sh)
export PATH="$(pwd)/reframe/bin:$PATH"

#
# Install Tests
#

git_repo_name=$(basename ${RFM_TESTS_GIT##* } .git)

log "clone ReFrame tests ${git_repo_name}"
rm -rf ${git_repo_name}
git clone ${RFM_TESTS_GIT} ${git_repo_name} && cd ${git_repo_name}

#
# Grab the meta data from the uenv image
#

squashfs-mount ${UENV}:${STACK_MOUNT} -- cat ${STACK_MOUNT}/meta/recipe/extra/reframe.yaml > ${UENV_REFRAME_META}

#
# Start ReFrame
#

: ${UENV:=${squashfs_path}:${mount}}
: ${RFM_AUTODETECT_METHODS:="cat /etc/xthostname,hostname"}
: ${RFM_USE_LOGIN_SHELL:=1}

export UENV
export RFM_AUTODETECT_METHODS
export RFM_USE_LOGIN_SHELL

REFRAME_COMMAND="reframe $(xargs <<< ${CHECKS}) --report-junit=$REPORT -r --system=${RFM_SYSTEM}"

log "running reframe: ${REFRAME_COMMAND}"
${REFRAME_COMMAND}
exitcode=$?


#
#
#

if [ "$exitcode" -eq 0 ];
then
    report_path=$(find -type f -name ${REPORT})
    log "report generated in $report_path"
    cat $report_path
else
    err "Reframe test run failed - no report artifact pushed"
fi

deactivate

exit ${exitcode}
