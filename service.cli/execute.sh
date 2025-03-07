#!/bin/sh
# set sh strict mode
set -o errexit
set -o nounset
IFS=$(printf '\n\t')

cd /home/scu/src/pymorphosonic

echo "starting service as"
echo   User    : "$(id "$(whoami)")"
echo   Workdir : "$(pwd)"
echo "..."
echo

# ----------------------------------------------------------------

env
python3 main.py setup
/bin/sh main.sh
python3 main.py teardown