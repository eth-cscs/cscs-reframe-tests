#!/bin/bash

set -euo pipefail

# this script will keep the minimum amount of files,
# it can be improved but this will do the job as is.
#
# Every delete runs in a subshell after a checked cd: a missing directory
# aborts the script instead of deleting files in $PWD or $OLDPWD.

dirn=${1:-}
# example: 'cuda-samples/cpp/1_Utilities/deviceQuery'
if [ -z "$dirn" ] ; then
    exit 1
else
    echo "cleaning $dirn"
fi

if [ ! -d "$dirn" ] ; then
    echo "_clean.sh: $dirn not found" >&2 ; exit 1
fi

IFS=/ read -r _top _layout _category _sample _rest <<< "$dirn"
if [ -z "$_sample" ] || [ -n "$_rest" ] ; then
    echo "_clean.sh: expected <repo>/<layout>/<category>/<sample>" >&2
    exit 1
fi

rm -fr "$_top/bin/win64"

# delete everything in $1 except CMakeLists.txt and $2
_prune() {
    (
        cd "$1"
        find . -mindepth 1 -maxdepth 1 \
            ! -name CMakeLists.txt \
            ! -name "$2" \
            -print -exec rm -fr {} +
    )
}

# --- level1: cuda-samples/cpp/, keep 1_Utilities
_prune "$_top/$_layout" "$_category"

# --- level2: cuda-samples/cpp/1_Utilities/, keep deviceQuery
_prune "$_top/$_layout/$_category" "$_sample"
