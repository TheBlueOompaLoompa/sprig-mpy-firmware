#!/usr/bin/env bash

compile_dir() {
    for f in $1/*; do
        if [[ $f == *.py ]]; then

            if [[ $f != *boot.py ]]; then
                mpy-cross -march=armv6m $f
                rm $f
            fi
        fi
        if [ -d "$f" ]; then
            compile_dir $f
        fi
    done
}

mkdir -p build
rm -rf build/*
cp -r src/* build/
compile_dir build
