#!/bin/bash
# DreamHost setup for statistics.
export TZ=PST8PDT
#export PYTHONPATH="$HOME/python:$PYTHONPATH"

# Ensure we're in the right virtual environment
export VIRTUAL_ENV_DISABLE_PROMPT=1
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib
. ~/python2.7.11/bin/activate


# Even if we're running in a weird shell, let's use THIS directory as the current directory
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
data="$SCRIPTPATH/data"
cd "$data"   # Run in the data directory.

touch hourly       # We were here!
# Handle training reports
cd "$SCRIPTPATH"
./dotraining101.sh
exit 0

        
# Copy info from Dropbox
(cd data; ../copywebfiles.py)
