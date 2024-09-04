#!/bin/bash

if [ -z $DEBUG ] ; then export DEBUG="n" ;fi
if [ $DEBUG = "y" ] ; then
    echo DEBUG=$DEBUG
    oras_tmp="$PWD"
    oras="uenv-oras"
    rfm_meta_yaml="$oras_tmp/meta/extra/reframe.yaml"
    jfrog_creds_path="${oras_tmp}/docker/config.json"
    system="$CLUSTER_NAME" ;
    if [ $system = "todi" ] ;then uarch="gh200" ;fi
    if [ $system = "eiger" ] ;then uarch="zen2" ;fi
    jfrog=jfrog.svc.cscs.ch/uenv/deploy/$system/$uarch
    jfrog_u="piccinal"
else
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
fi

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
  uenv_repo=https://github.com/eth-cscs/uenv
  uenv_version=5.1.0
  (wget --quiet $uenv_repo/archive/refs/tags/v$uenv_version.tar.gz && \
  tar xf v$uenv_version.tar.gz && cd uenv-$uenv_version/ && \
  echo N | ./install --prefix=$PWD --local && \
  rm -f v$uenv_version.tar.gz uenv-$uenv_version)
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
# {{{ uenv_pull_meta_dir
uenv_pull_meta_dir() {
    img=$1
    echo "--- Pulling metadata from $img"
    uenv image pull --only-meta $img &> uenv_pull_meta_dir.log
}    
# }}}    
# {{{ oras_pull_meta_dir
oras_pull_meta_dir() {
    img=$1
    name=`echo "$img" |cut -d: -f1`
    tag=`echo "$img" |cut -d: -f2`
    echo "--- Pulling metadata from $jfrog/$name:$tag"
    # meta_digest=`$oras --registry-config $jfrog_creds_path \
    rm -fr meta # remove dir from previous image
    meta_digest=`$oras discover --output json --artifact-type 'uenv/meta' $jfrog/$name:$tag \
        | jq -r '.manifests[0].digest'`
    # $oras --registry-config $jfrog_creds_path \
    echo "---- $jfrog/$name@$meta_digest"
    $oras pull --output "${oras_tmp}" "$jfrog/$name@$meta_digest" &> oras-pull.log
}
# }}}
# {{{ meta_has_reframe_yaml
meta_has_reframe_yaml() {
    img=$1
    echo "# --- Checking img=$img for meta/extra/reframe.yaml"
    meta_path=`uenv image inspect --format {meta} $img`
    echo "meta_path=$meta_path"
    rfm_yaml="${meta_path}/extra/reframe.yaml" 
    test -f $rfm_yaml ; rc=$?
    
    # --- VASP
    is_vasp=`echo $img |cut -d/ -f1`
    if [ "$is_vasp" == "vasp" ] ;then
        echo "# ---- no: vasp is a special case: "todi/gh200/vasp/v6.4.2/manifests/v1": response status code 403: Forbidden"
    else

    if [ $rc -eq 0 ] ;then
        rctools=$(grep -q user-tools $rfm_yaml ; echo $?)
        echo "rc=$rc rctools=$rctools"
        if [ $rctools -ne 0 ] ;then
            echo "# ---- reframe.yaml has been found --> pulling $img"
            uenv image pull $img
            echo
            # meta/extra/reframe.yaml
            # echo "# ---- reframe.yaml has been found --> adding it as store.yaml"
            # imgpath=`uenv image inspect $img --format {path}`
            # cp $rfm_yaml $imgpath/store.yaml

            # TODO: https://github.com/eth-cscs/alps-uenv/issues/127 <-------------
            if [ "$img" == "prgenv-gnu/24.7:v1" ] ;then
                sed -i 's-default/activate.sh-develop/activate.sh-' \
                    $imgpath/store.yaml
            fi
            # TODO: https://github.com/eth-cscs/alps-uenv/issues/127 <-------------

            echo "# ---- OK $rfm_yaml found in $img :-)"
            ls $rfm_yaml
        fi
    else
        echo "# ---- no $rfm_yaml file found, skipping $img :-("
    fi
    fi
}
# }}}
# {{{ remove_last_comma_from_variable
remove_last_comma_from_variable() {
    vv=$1
    vv=${vv%?}
    echo ${vv} | sed 's-,,-,-g' | sort -u
    #echo "UENV=$UENV" > rfm_uenv.env
    #cat rfm_uenv.env | tr , "\n"
}
# }}}
# {{{ oras_pull_meta_dir_old
oras_pull_meta_dir_old() {
    img=$1
    echo "----- Pulling img=$img metadata & sqfs"
    name=`echo "$img" |cut -d: -f1`
    tag=`echo "$img" |cut -d: -f2`
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
            imgpath=`uenv image inspect $img --format {path}`
            cp $rfm_yaml $imgpath/store.yaml
            # echo "ok"
            return 0
        else
            echo "failed to find $rfm_yaml file in $img"
            return 1
        fi
    else
        echo "failed to download $jfrog/$name@$meta_digest"
        return 2
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
    # deps for cscs-reframe-tests.git:
    pip install python-hostlist requests &> .deps.cscs-reframe-tests
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
# {{{ launch_reframe_1arg
launch_reframe_1arg() {
    export RFM_AUTODETECT_METHODS="cat /etc/xthostname,hostname"
    export RFM_USE_LOGIN_SHELL=1
    # export RFM_AUTODETECT_XTHOSTNAME=1
    # reframe -V
    echo "UENV=$UENV"
    echo "# img=$img"
    reframe -C ./config/cscs.py \
        --report-junit=report.xml \
        $img \
        --system=$system \
        -r
}
# }}}
# {{{ oneuptime
oneuptime() {
    # source rfm_venv/bin/activate
    CLUSTER_NAME=$1
    PE=$2
    echo "CLUSTER_NAME=$CLUSTER_NAME"
    if [ -f 'reframe.out' ] ; then grep 'FAILURE INFO for' reframe.out ; fi
    json_rpt='latest.json'
    if [ -f $json_rpt ] ; then
        num_failures=`grep -m1 num_failures $json_rpt |cut -d: -f2 |cut -d, -f1 |tr -d " "`
    else
        num_failures=-1
        echo "# warning: no json_rpt=$json_rpt file found"
    fi
    echo "Updating oneuptime status page"
    python3 ./ci/scripts/oneuptime.py $CLUSTER_NAME $num_failures $PE
}
# }}}

# {{{ main 
in="$1"
img="$2"
pe="$3"
case $in in
    setup_jq) setup_jq;;
    setup_uenv_and_oras) setup_uenv_and_oras;;
    setup_oras_without_uenv) setup_oras_without_uenv;;
    check_uenv_oras) check_uenv_oras;;
    jfrog_login) jfrog_login "$jfrog_creds_path";;
    uenv_image_find) uenv_image_find;;
    oras_pull_meta_dir) oras_pull_meta_dir "$img";;
    uenv_pull_meta_dir) uenv_pull_meta_dir "$img";;
    meta_has_reframe_yaml) meta_has_reframe_yaml "$img";;
    remove_last_comma_from_variable) remove_last_comma_from_variable "$myvar";;
    oras_pull_sqfs) oras_pull_sqfs;;
    uenv_pull_sqfs) uenv_pull_sqfs "$img";;
    install_reframe) install_reframe;;
    install_reframe_tests) install_reframe_tests;;
    uenv_sqfs_fullpath) uenv_sqfs_fullpath "$img";;
    launch_reframe_1img) launch_reframe_1img "$img";;
    launch_reframe) launch_reframe;;
    launch_reframe_1arg) launch_reframe_1arg "$img";;
    oneuptime) oneuptime "$img" "$pe";;
    *) echo "unknown arg=$in";;
esac
#old [[ -d $oras_tmp ]] && { echo "cleaning $oras_tmp"; rm -fr $oras_tmp; }
# }}} 
