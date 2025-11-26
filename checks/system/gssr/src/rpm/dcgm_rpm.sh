#!/bin/bash

# test1:
which dcgmi

# test2:
export dcgmi_version=`dcgmi --version |grep version |awk '{print $3}'`
shasum /usr/lib64/*dcgm* &> _${dcgmi_version}.rpt
diff -s ${dcgmi_version}.ref _${dcgmi_version}.rpt
