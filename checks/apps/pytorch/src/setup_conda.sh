#!/bin/bash -l
INSTALL_PATH=${1:-$PWD/forge}

# Download and install conda
wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh -b -p $INSTALL_PATH
. $INSTALL_PATH/etc/profile.d/conda.sh
export PATH=$INSTALL_PATH/bin:$PATH
