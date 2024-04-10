#!/usr/bin/env bash
unset CDPATH; cd "$( dirname "${BASH_SOURCE[0]}" )"; cd "$(pwd -P)"
cd ..

#
# Place any cluster-specific commands here...
#


#
# End cluster-specific block
#

source "settings/credentials.sh"

# Logfile location
logfile="$PWD/logs/hpc_client.log"

# Ensure that user environment is loaded
USER=$(whoami)
source /home/$USER/.bashrc

# Launch cast
# Using "timeout" prevents the script hanging when launched automatically.
# This time limit may need to be adjusted based on the speed of your system.
# Depending on the choice of Python environments, you may need to activate the
# environment before running hpc-client. For example, if you are using a
# pipenv environment, you may need to use the following command:
# timeout 5m python3 -m pipenv run fw-hpc-client "$@" 2>&1 | tee -a "$logfile"
timeout 5m fw-hpc-client "$@" 2>&1 | tee -a "$logfile"
