#!/bin/bash

in=$1


ntests=`jq .runs[0].testcases[].job_exitcode $in |wc -l |awk '{print $0-1}'`

echo "# result aos fp64 h5part tipsy testname reason basename"
for ii in `seq 0 $ntests` ;do
# for ii in `seq 0 2` ;do
    result=`jq -r .runs[0].testcases[$ii].result $in`
    aos=`jq -r .runs[0].testcases[$ii].aos $in`
    fp64=`jq -r .runs[0].testcases[$ii].fp64 $in`
    tipsy=`jq -r .runs[0].testcases[$ii].tipsy $in`
    h5part=`jq -r .runs[0].testcases[$ii].h5part $in`
    testname=`jq -r .runs[0].testcases[$ii].test $in`
    # stagedir=`jq -r .runs[0].testcases[$ii].stagedir $in`
    basename=`jq -r .runs[0].testcases[$ii].stagedir $in |xargs basename`
    fail_reason=`jq -r .runs[0].testcases[$ii].fail_reason $in`
    if [ "$fail_reason" = "null" ] ;then reason=pass ;else reason=$fail_reason ;fi

    echo "$result $aos $fp64 $tipsy $h5part $testname \"$reason\" $basename"
done
