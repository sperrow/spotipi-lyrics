#!/bin/bash
# Source this file to load .spotipi-config environment variables
# Usage: source ./load-config.sh

if [ -f .spotipi-config ]; then
    export "$(cat .spotipi-config | grep -v '^#' | xargs)"
else
    echo "Error: .spotipi-config not found"
    exit 1
fi
