#!/bin/bash
# DreamHost setup for statistics.
export TZ=PST8PDT
export I_AM_D101TM=1
#export PYTHONPATH="$HOME/python:$PYTHONPATH"

# Ensure we're in the right virtual environment
#export VIRTUAL_ENV_DISABLE_PROMPT=1
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib
#. ~/python2.7.11/bin/activate


# Even if we're running in a weird shell, let's use THIS directory as the current directory
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
cd "$SCRIPTPATH"

./daily.sh "$*"
./hourly.sh "$*"

