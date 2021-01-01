#!/bin/bash
# DreamHost setup for statistics.
export TZ=PST8PDT
export I_AM_D101TM=1

# Even if we're running in a weird shell, let's use THIS directory as the current directory
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
cd "$SCRIPTPATH"

./daily.sh "$*"
./hourly.sh "$*"

