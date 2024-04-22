#!/bin/bash

# {{{ input parameters <--- 
# oras="$UENV_PREFIX/libexec/uenv-oras"  # /users/piccinal/.local/ on eiger
# oras_tmp=`mktemp -d`
oras_tmp=$PWD
oras="$oras_tmp/oras"
# oras_path=`mktemp -d`
rfm_meta_yaml="$oras_tmp/meta/extra/reframe.yaml"
# artifact_path=$PWD  # "$oras_tmp"
jfrog_creds_path="${oras_tmp}/docker/config.json"
jfrog_request="$CSCS_CI_MW_URL/credentials?token=$CI_JOB_TOKEN&creds=container_registry"
# system="santis" ; uarch="gh200"
system="eiger" ; uarch="zen2"
#del name=`echo $in |cut -d: -f1`
#del tag=`echo $in |cut -d: -f2`
#del jfrog=jfrog.svc.cscs.ch/uenv/deploy/$system/$uarch/$name
jfrog=jfrog.svc.cscs.ch/uenv/deploy/$system/$uarch
jfrog_u="piccinal"
[[ -z "${SLURM_PARTITION}" ]] && RFM_SYSTEM="${system}" || RFM_SYSTEM="${system}:${SLURM_PARTITION}"
# }}}

# {{{ setup_oras 
setup_oras() {
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
# {{{ setup_jq 
setup_jq() {
  # cd $oras_tmp 
  wget --quiet https://github.com/jqlang/jq/releases/download/jq-1.6/jq-linux64
  chmod 700 jq-linux64
  mv jq-linux64 jq
  ./jq --version
}
# }}}
# {{{ setup_uenv 
setup_uenv() {
  # cd $oras_tmp 
  uenv_repo=https://github.com/eth-cscs/uenv
  uenv_version=4.0.1
  (wget --quiet $uenv_repo/archive/refs/tags/v$uenv_version.tar.gz && \
  tar xf v$uenv_version.tar.gz && cd uenv-$uenv_version/ && \
  echo N | ./install --prefix=$PWD --local && \
  rm -f v$uenv_version.tar.gz uenv-$uenv_version)
  # ls -lrt bin/activate-uenv
  # /users/piccinal/cscs-reframe-tests.git/ci/DEL/uenv/bin/activate-uenv
  # ./jq --version
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
    uenv image find |grep -v 'uenv/version:' |awk '{print $1}'
}
# }}}
# {{{ oras_pull_meta 
oras_pull_meta_dir() {
    name=$1
    tag=$2
    #
    meta_digest=`$oras --registry-config $jfrog_creds_path \
    discover --output json --artifact-type 'uenv/meta' $jfrog/$name:$tag \
    | jq -r '.manifests[0].digest'`
    #
    $oras --registry-config $jfrog_creds_path \
    pull --output "${oras_tmp}" "$jfrog/$name@$meta_digest"
    #
    [[ $? -eq 0 ]] || { echo "failed to download $jfrog/$name@$meta_digest, exiting"; exit 1; }
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
    rm -fr rfm_venv reframe
    python3 -m venv rfm_venv
    source rfm_venv/bin/activate
    # pip install --upgrade reframe-hpc
    git clone -b v4.5.2 --depth 1 https://github.com/reframe-hpc/reframe.git
    (cd reframe; ./bootstrap.sh)
    # TODO: https://github.com/reframe-hpc/reframe/archive/refs/tags/v4.5.2.tar.gz
    # (cd reframe; git checkout v4.5.0; ./bootstrap.sh)
    export PATH="$(pwd)/reframe/bin:$PATH"
}    
# }}}
# {{{ install_reframe_tests (alps branch) 
install_reframe_tests() {
    rm -fr cscs-reframe-tests
    git clone -b alps https://github.com/eth-cscs/cscs-reframe-tests.git
}
# }}}
# {{{ launch_reframe 
launch_reframe() {
    export UENV="${squashfs_path}:${mount}"
    export RFM_AUTODETECT_METHODS="cat /etc/xthostname,hostname"
    export RFM_USE_LOGIN_SHELL=1
    # reframe -C cscs-reframe-tests/config/cscs.py --report-junit=report.xml -c cscs-reframe-tests/checks/ -r --system=${RFM_SYSTEM}
    reframe -V
}
# }}}

# {{{ main
in=$1
case $in in
    setup_oras) setup_oras;;
    setup_uenv) setup_uenv;;
    setup_jq) setup_jq;;
    check_uenv_oras) check_uenv_oras;;
    jfrog_login) jfrog_login "$jfrog_creds_path";;
    *) echo "unknown arg=$in";;
esac
#old pwd
#old ls -la
#old check_uenv_oras
#old echo
#old 
#old jfrog_login "$jfrog_creds_path" # "$jfrog_u" "$XXX"
#old echo
#old 
#old imgs=`uenv_image_find`
#old # echo $imgs
#old # for ii in `echo $imgs |cut -d" " -f1` ;do e $ii ;done
#old img0=`echo $imgs |cut -d" " -f1`
#old name=`echo $img0 |cut -d: -f1`
#old tag=`echo $img0 |cut -d: -f2`
#old oras_pull_meta_dir $name $tag
#old echo
#old 
#old uenv_pull_sqfs "$name:$tag"
#old echo
#old 
#old install_reframe
#old echo
#old 
#old install_reframe_tests
#old echo
#old 
#old launch_reframe
#old echo
#old # set -x
#old # set +x
#old 
#old [[ -d $oras_tmp ]] && { echo "cleaning $oras_tmp"; rm -fr $oras_tmp; }
# }}}

# TODO: oras attach rpt
