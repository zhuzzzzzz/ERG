#!/bin/bash

script_abs=$(readlink -f "$0")
script_dir=$(dirname $script_abs)

# export log file name

echo "Do not close, Running iocLogServer..."
iocLogServer
