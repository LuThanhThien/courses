#!/bin/bash


ISPC_PATH="/mnt/c/Users/admin/OneDrive - 보스반도체/Courses/CS149 Standford - Parallel Computing/assignments/ispc-v1.21.0-linux/bin"

# Check if the path is already in the PATH
if [[ ":$PATH:" != *":$ISPC_PATH:"* ]]; then
    echo "Adding ISPC path to PATH."
    export PATH="$PATH:$ISPC_PATH"
else
    echo "ISPC path already in PATH."
fi
