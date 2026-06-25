#!/bin/bash

tst=$1
ref=$2
new=$3

if [ -z "$tst" ]; then echo "undefined tst=$tst" ; exit 1; fi
if [ -z "$ref" ]; then echo "undefined ref=$ref" ; exit 1; fi
if [ -z "$new" ]; then echo "undefined new=$new" ; exit 1; fi

case "$tst" in
  rmse)
      # normalized RMSE should be close to 0 (0 = identical, 1 = completely different)
      # and 1-rmse should be close to 1:
      #   |     1-rmse     | 1-rmse |
      #   |----------------|--------|
      #   0     not OK    tol  OK   1
      tol=0.95
      one_rmse=$(magick compare -metric RMSE $ref $new null: |& awk -F'[()]' '{ print 1-$2 }')
      echo "1-rmse=$one_rmse"
      echo $one_rmse | awk -v tol=$tol -v ref=$ref -v new=$new '{if ($0>=tol) {print ref" and "new" are identical"} else {print ref" and "new" differ"}}'
      ;;
  visual)
      # it will return either: "Files ... are identical" or "Files ... differ (<number of different pixels>)"
      echo -n "Files ${ref} vs ${new} "
      pixel_diff=$(magick compare -metric AE $ref $new null: 2>&1)
      if [[ ${pixel_diff} == 0 ]]
      then
        echo "are identical"
      else
        echo "differ (${pixel_diff})"
      fi
      ;;
  binary|*)
      # diff will return either: "Files ... are identical" or "Files ... differ"
      diff -s $ref $new
      ;;
esac
