#!/usr/bin/env bash

mkdir -p build
rm -rf build/*
cp -r src/* build/
for f in build/*; do
    if [[ $f == *.py ]]
    then
        mpy-cross -march=armv6m $f
        rm $f
    fi
done
