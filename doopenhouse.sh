#!/bin/sh
# DreamHost setup for statistics.
export TZ=PST8PDT
export PYTHONPATH="$HOME/python:$PYTHONPATH"

# Ensure we're in the right virtual environment
export VIRTUAL_ENV_DISABLE_PROMPT=1
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib
[[ -e ~/python2.7.11/bin ]] && . ~/python2.7.11/bin/activate


# Even if we're running in a weird shell, let's use THIS directory as the current directory
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
data="$SCRIPTPATH/data"
cd "$data"   # Run in the data directory.

export STATS_HOME="$SCRIPTPATH"
export STATS_DATA="$STATS_HOME/data"
echo "<p>Getting new roster</p>"
../getroster.sh
echo "<p>Processing Open House Report</p>"
echo "<pre>"
../openhouse.py && cp openhouseclubs.html ~/files/reports/
echo "</pre>"
echo "<p>Open House Report has been updated on the <a href="/district-programs#openhousechallenge">District Programs</a> page.</p>"

