#!/bin/bash

# This script will compare the .png file created by Ascent with a reference
# .png file: normalized RMSE should be close to 0 (0 = identical, 1 =
# completely different) and 1-rmse should be close to 1:
#   |     1-rmse     | 1-rmse |
#   |----------------|--------|
#   0     not OK    tol  OK   1

tst=$1
ref=$2
new=$3
tol=0.9999961703

if [ -z $tst ]; then echo "undefined tst=$tst" ; exit -1; fi
if [ -z $ref ]; then echo "undefined ref=$ref" ; exit -1; fi
if [ -z $new ]; then echo "undefined new=$new" ; exit -1; fi

case "$tst" in
  ascent_first_light_example|ascent_scene_example1|ascent_trigger_example1)
      # 0.250977 (3.82966e-06) -> 1-rmse=0.9999961703 ok
      one_rmse=$(magick compare -metric RMSE $ref $new null: |& sed -e "s-(--" -e "s-)--" |awk '{printf "%.10f", 1-$2}')
      echo "1-rmse=$one_rmse"
      echo $one_rmse |awk -v tol=$tol -v ref=$ref -v new=$new '{if ($0>=tol) {print ref" and "new" are identical"} else {print ref" and "new" differ"}}'
      ;;
  *)
      # diff will return either: "Files ... are identical" or "Files ... differ"
      diff -s $ref $new
      ;;
esac
