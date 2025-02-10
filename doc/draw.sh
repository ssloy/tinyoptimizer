#!/bin/bash

for ll in `ls -1 *.ll`; do
    opt -passes=dot-cfg -disable-output -cfg-dot-filename-prefix=`basename $ll .ll` $ll
done

for f in `ls -1 *.dot`; do
    dot -Tpng $f -O
done
