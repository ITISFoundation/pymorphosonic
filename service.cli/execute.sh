#!/bin/bash
# set sh strict mode
set -o errexit
set -o nounset
IFS=$(printf '\n\t')
INFO="INFO: [$(basename "$0")] "

cd /home/smu/osparc_python_runner

echo "$INFO" "starting service as"
echo "$INFO" "  User    :$(id "$(whoami)")"
echo "$INFO" "  Workdir : $(pwd)"

echo "$INFO" "activating sim4life venv $SC_VENV"
source $SC_VENV/bin/activate

which python
python --version

echo "$INFO" "creating smu venv $SC_PYTHON_VENV_ROOT_DIR"
virtualenv -p "$SC_VENV"/bin/python "$SC_PYTHON_VENV_ROOT_DIR"
realpath "$SC_VENV"/lib/python3.11/site-packages >  "$SC_PYTHON_VENV_ROOT_DIR"/lib/python3.11/site-packages/base_venv.pth

echo "$INFO" "activating smu venv $SC_PYTHON_VENV_ROOT_DIR"
source "$SC_PYTHON_VENV_ROOT_DIR"/bin/activate

# Checking for resources limit env vars injected by osparc
SIMCORE_NANO_CPUS_LIMIT="${SIMCORE_NANO_CPUS_LIMIT:-0}"
if [ "${SIMCORE_NANO_CPUS_LIMIT}" -ne "0" ]
then
    echo "$INFO" "Found NANO_CPU limits: ${SIMCORE_NANO_CPUS_LIMIT}"
    NANO_CPU_DIVISOR=1000000000
    MAX_CPUS=$(("${SIMCORE_NANO_CPUS_LIMIT}" / "${NANO_CPU_DIVISOR}"))
    # use 1 if this is 0 otherwise floor is probably fine
    if [ "${MAX_CPUS}" -eq "0" ]
    then
        MAX_CPUS=1
    fi
    echo "$INFO" "Setting Z43_MAX_CPU_RESOURCES to " "${MAX_CPUS}"
    export Z43_MAX_CPU_RESOURCES="${MAX_CPUS}"
    export OMP_NUM_THREADS="${MAX_CPUS}"
fi

env

python3 main.py setup
/bin/sh main.sh
python3 main.py teardown
