#!/usr/bin/env bash
./setup.sh
source bin/activate
nodemon -w src -e py --exec ./compile.sh
