#!/bin/bash

# {{{ input parameters <--- 
# oras="$UENV_PREFIX/libexec/uenv-oras"  # /users/piccinal/.local/ on eiger
# oras_tmp=`mktemp -d`
oras_tmp=$PWD
oras="uenv-oras"
# oras_path=`mktemp -d`
rfm_meta_yaml="$oras_tmp/meta/extra/reframe.yaml"
# artifact_path=$PWD  # "$oras_tmp"
jfrog_creds_path="${oras_tmp}/docker/config.json"
jfrog_request="$CSCS_CI_MW_URL/credentials?token=$CI_JOB_TOKEN&job_id=$CI_JOB_ID&creds=container_registry"
# jfrog_request_nojobid="$CSCS_CI_MW_URL/credentials&token=$CI_JOB_TOKEN&creds=container_registry"
# https://cicd-ext-mw.cscs.ch/ci
# system="santis" ; uarch="gh200"
# FIRECREST_SYSTEM=santis UARCH=gh200
system="$FIRECREST_SYSTEM" ; uarch="$UARCH"
#del name=`echo $in |cut -d: -f1`
#del tag=`echo $in |cut -d: -f2`
#del jfrog=jfrog.svc.cscs.ch/uenv/deploy/$system/$uarch/$name
jfrog=jfrog.svc.cscs.ch/uenv/deploy/$system/$uarch
jfrog_u="piccinal"
[[ -z "${SLURM_PARTITION}" ]] && RFM_SYSTEM="${system}" || RFM_SYSTEM="${system}:${SLURM_PARTITION}"
 # }}}

# {{{ setup_jq 
setup_jq() {
  if [ ! -x /usr/bin/jq ] ;then
    wget --quiet https://github.com/jqlang/jq/releases/download/jq-1.6/jq-linux64
    chmod 700 jq-linux64
    mv jq-linux64 jq
    ./jq --version
  fi
}
# }}}
# {{{ setup_uenv_and_oras 
setup_uenv_and_oras() {
  # cd $oras_tmp 
  if [ -z $UENV_PREFIX ] ;then
    uenv_repo=https://github.com/eth-cscs/uenv
    uenv_version=4.0.1
    (wget --quiet $uenv_repo/archive/refs/tags/v$uenv_version.tar.gz && \
    tar xf v$uenv_version.tar.gz && cd uenv-$uenv_version/ && \
    echo N | ./install --prefix=$PWD --local && \
    rm -f v$uenv_version.tar.gz uenv-$uenv_version)
  fi    
  # source ./uenv-4.0.1/bin/activate-uenv
  # export oras="$UENV_PREFIX/libexec/uenv-oras"
}
# }}}
# {{{ setup_oras_without_uenv 
setup_oras_without_uenv() {
  case "$(uname -m)" in
    aarch64)
      get_arch="arm64"
      ;;
    *)
      get_arch="amd64"
      ;;
  esac

  oras_arch=$get_arch
  oras_version=1.1.0
  oras_file=oras_${oras_version}_linux_${oras_arch}.tar.gz
  oras_url=https://github.com/oras-project/oras/releases/download/v${oras_version}/${oras_file}
  (wget --quiet "$oras_url" && tar zxf $oras_file && rm -f *.tar.gz)
  # export PATH="$oras_tmp:$PATH"
  # echo $PWD
  ./oras version
}
# }}}
# {{{ check_uenv_oras 
check_uenv_oras() {
    # [[ -x $UENV_PREFIX ]] || { echo "UENV_PREFIX=$UENV_PREFIX is not set, exiting"; exit 1; }
    # [[ -x $UENV_PREFIX/libexec/uenv-oras ]] || { echo "uenv-oras not found, exiting"; exit 1; }
    [[ -x $UENV_CMD ]] || { echo "UENV_CMD=$UENV_CMD is not set, exiting"; exit 1; }
    [[ -x $oras ]] || { echo "oras=$oras not found, exiting"; exit 1; }
}
# }}}
# {{{ jfrog_login 
jfrog_login() {
    creds_json=$(curl --retry 5 --retry-connrefused --fail --silent "$jfrog_request")
    oras_creds="$(echo ${creds_json} | jq --join-output '"--username " + .container_registry.username + " --password " +.container_registry.password')"
    jfrog_u="$(echo ${creds_json} | jq -r '.container_registry.username')"
    jfrog_p="$(echo ${creds_json} | jq -r '.container_registry.password')"
    ## Create a unique credentials path for this job,
    ## because by default credentials are stored in ~/.docker/config.json which
    ## causes conflicts for concurrent jobs (https://github.com/eth-cscs/alps-uenv)
    jfrog_creds_path="$1"
    # jfrog_u="$2"
    # jfrog_p="$3"
    echo "${jfrog_p}" | $oras login -v --registry-config ${jfrog_creds_path} \
    jfrog.svc.cscs.ch --username "${jfrog_u}" --password-stdin
    [[ $? -eq 0 ]] || { echo "failed oras login to JFrog, exiting"; exit 1; }
    # eiger:
    #  sarus run -t python bash
    #  oras login -v jfrog.svc.cscs.ch --username piccinal
    #  oras discover -v --output json --artifact-type 'uenv/meta' jfrog.svc.cscs.ch/uenv/deploy/eiger/zen2/prgenv-gnu/23.11:latest
    #  oras discover -v --output json --artifact-type 'uenv/meta' jfrog.svc.cscs.ch/uenv/deploy/santis/gh200/linaro-forge/23.1.2:latest
}
# }}}
# {{{ uenv_image_find 
uenv_image_find() {
    uenv --no-color image find | grep -v "uenv/version:tag" | awk '{print $1}'
}
# }}}
# {{{ oras_pull_meta_dir
oras_pull_meta_dir() {
    img=$1
    name=`echo "$img" |cut -d: -f1`
    tag=`echo "$img" |cut -d: -f2`
    #
    # meta_digest=`$oras --registry-config $jfrog_creds_path \
    rm -fr meta  # remove dir from previous image
    meta_digest=`$oras discover --output json --artifact-type 'uenv/meta' $jfrog/$name:$tag \
    | jq -r '.manifests[0].digest'`
    #
    # $oras --registry-config $jfrog_creds_path \
    $oras pull --output "${oras_tmp}" "$jfrog/$name@$meta_digest" &> oras-pull.log
    rc1=$?
    # echo "rc1=$rc1"
    rfm_yaml="${oras_tmp}/meta/extra/reframe.yaml" 
    if [ $rc1 -eq 0 ] ;then
        # find "${oras_tmp}" -name reframe.yaml
        test -f $rfm_yaml
        rc2=$?
        # echo "rc2=$rc2"
        if [ $rc2 -eq 0 ] ;then
            echo "ok"
        else
            echo "failed to find $rfm_yaml file in $img"
        fi
    else
        echo "failed to download $jfrog/$name@$meta_digest"
    fi
}
# }}}
# {{{ oras_pull_sqfs 
oras_pull_sqfs() {
    name=$1
    tag=$2
    #
    t0=`date +%s`
    $oras pull --registry-config ${jfrog_creds_path} \
    --output "${artifact_path}" $jfrog/$name:$tag
    #
    [[ $? -eq 0 ]] || { echo "failed to download squashfs image, exiting"; exit 1; }
    t1=`date +%s`
    tt=`expr $t1 - $t0`
    echo "t(pull) = $tt seconds"
    #
    squashfs_path="${artifact_path}/store.squashfs"
    echo "$squashfs_path"
}   
# }}}
# {{{ uenv_pull_sqfs 
uenv_pull_sqfs() {
# image 1e2d418fe383f793449e61e64c3700de4a07822ee16a89573d78f5e59a781519 is already available locally
# updating local reference prgenv-gnu/23.11:latest
# image available at /capstor/scratch/cscs/piccinal/.uenv-images/images/1e2d418fe383f793449e61e64c3700de4a07822ee16a89573d78f5e59a781519/store.squashfs
    img="$1"
    [[ -f "${rfm_meta_yaml}" ]] || { echo "$rfm_meta_yaml missing, skipping $img"; }
    t0=`date +%s`
    uenv image pull $img
    [[ $? -eq 0 ]] || { echo "failed to download squashfs image with uenv, exiting"; exit 1; }
    t1=`date +%s`
    tt=`expr $t1 - $t0`
    echo "t(pull) = $tt seconds"
    #
    squashfs_path=`uenv image inspect $img --format {path}`
    cp $rfm_meta_yaml $squashfs_path/store.yaml
    ls -l $squashfs_path/
}   
# }}}
# {{{ install_reframe 
install_reframe() {
    # all must be quiet because of last echo
    rm -fr rfm_venv reframe
    python3 -m venv rfm_venv
    source rfm_venv/bin/activate
    # pip install --upgrade reframe-hpc
    # git clone --depth 1 https://github.com/reframe-hpc/reframe.git
    # multi-uenv support only in reframe > v4.5.2:
    (wget --quiet "https://github.com/reframe-hpc/reframe/archive/refs/heads/develop.zip" && \
    unzip -qq "develop.zip" && cd reframe-develop && ./bootstrap.sh &> /dev/null)
    export PATH="$(pwd)/reframe-develop/bin:$PATH"
    echo "$(pwd)/reframe-develop/bin"
    # (wget --quiet "https://github.com/reframe-hpc/reframe/archive/refs/tags/v4.5.2.tar.gz" && \
    # tar xf v4.5.2.tar.gz && \
    # cd reframe-4.5.2 && \
    # ./bootstrap.sh)
    # echo "$PWD/reframe-4.5.2/bin"
    # export PATH="$(pwd)/reframe/bin:$PATH"
}    
# }}}
# {{{ install_reframe_tests (alps branch) 
install_reframe_tests() {
    rm -fr cscs-reframe-tests
    git clone -b alps https://github.com/eth-cscs/cscs-reframe-tests.git
    pip install python-hostlist
    # TODO: pyfirecrest requires python>=3.7    
    # cscs-reframe-tests/config/utilities/requirements.txt
}
# }}}
# {{{ uenv_sqfs_fullpath
uenv_sqfs_fullpath() {
    img="$1"
    uenv image inspect $img --format {sqfs}
}   
# }}}
# {{{ launch_reframe_1img 
launch_reframe_1img() {
    img=$1
    # export UENV="${squashfs_path}:${mount}"
    export UENV="$img"
    export RFM_AUTODETECT_METHODS="cat /etc/xthostname,hostname"
    export RFM_USE_LOGIN_SHELL=1
    # export RFM_AUTODETECT_XTHOSTNAME=1
    # reframe -V
    reframe -C ./config/cscs.py --report-junit=report.xml -c ./checks/ \
    -r --system=$system
    # -n HelloWorldTestMPIOpenMP
}
# }}}
# {{{ launch_reframe 
launch_reframe() {
    export RFM_AUTODETECT_METHODS="cat /etc/xthostname,hostname"
    export RFM_USE_LOGIN_SHELL=1
    # export RFM_AUTODETECT_XTHOSTNAME=1
    # reframe -V
    echo "UENV=$UENV"
    reframe -C ./config/cscs.py \
        --report-junit=report.xml \
        -c ./checks/ \
        --system=$system \
        -r
    # -J reservation=all_nodes
    # -n HelloWorldTestMPIOpenMP
}
# }}}

# {{{ main 
in=$1
img=$2
case $in in
    setup_jq) setup_jq;;
    setup_uenv_and_oras) setup_uenv_and_oras;;
    setup_oras_without_uenv) setup_oras_without_uenv;;
    check_uenv_oras) check_uenv_oras;;
    jfrog_login) jfrog_login "$jfrog_creds_path";;
    uenv_image_find) uenv_image_find;;
    oras_pull_meta_dir) oras_pull_meta_dir "$img";;
    oras_pull_sqfs) oras_pull_sqfs;;
    uenv_pull_sqfs) uenv_pull_sqfs "$img";;
    install_reframe) install_reframe;;
    install_reframe_tests) install_reframe_tests;;
    uenv_sqfs_fullpath) uenv_sqfs_fullpath "$img";;
    launch_reframe_1img) launch_reframe_1img "$img";;
    launch_reframe) launch_reframe;;
    *) echo "unknown arg=$in";;
esac
#old [[ -d $oras_tmp ]] && { echo "cleaning $oras_tmp"; rm -fr $oras_tmp; }
# }}}

# TODO: oras attach rpt
