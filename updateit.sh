#!/bin/bash
# This program fetches the latest statistics from Toastmasters and
#    adds them to the database.
# Return Code is the OR of these:
#   0:  all fine
#   1:  no changes detected (includes 'already run today without force')
#   2:  club info not received
#   4:  performance info not received

# We also get educational achievements but the return code is unaffected.


# Even if we're running in a weird shell, let's use THIS directory as the current directory
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
cd "$SCRIPTPATH"
data="$SCRIPTPATH/data"

if [ ! -d "$data" ] ; then
    mkdir ""$data""  
fi

# Keep track of where we started
savedir="$(pwd)"

# We need to know today's date and yesterday's.
today=$(date +'%Y-%m-%d')
if ! yday=$(date -v-1d +'%Y-%m-%d' 2>/dev/null)
then
    yday=$(date -d '1 day ago' +'%Y-%m-%d' 2>/dev/null)
fi

cd "$data"

# Allow the run to happen even if we think things are up-to-date
# Also decide whether or not to zip up older files from Toastmasters.

if [ "$1" = "force" ]
then
    force="force"
    zip="zip"
elif [ "$1" = "test" ]
then
    force="force"
    zip=""
else
    force=""
    zip="zip"
fi

# If we have all of yesterday's performance files,
#   exit with RC=1 (no changes) (unless forced to run).

if [[ -z "$force" && -e "clubs.$yday.csv" && -e "clubperf.$yday.csv" && -e "areaperf.$yday.csv" && -e "distperf.$yday.csv" ]]
then
    exit 1
fi
let ret=0  # Assume all is well

# Get performance files, including latest club file from Toastmasters.
../getperformancefiles.py

# Note the file status
if [ ! -e "clubs.$yday.csv" ]
then
    let ret=ret+2
fi


if [[ ! ( -e "clubperf.$yday.csv" && -e "areaperf.$yday.csv" && -e "distperf.$yday.csv" ) ]]
then
    let ret=ret+4
fi


# Load them into the database
../loaddb.py
let ret=$ret+$?

# Update the lastfor table, normally for the last year, but if force, do all.
if [[ "$force" = "force" ]]
then
    ../populatelastfor.py
else
    ../populatelastfor.py --latestonly
fi

# Move old files to history unless otherwise requested
if [[ "$zip" = "zip" ]]
then
    year=${yday:0:4}
    zip -mT hist$year.zip clubs.$year*.csv clubperf.$year*.csv areaperf.$year*.csv distperf.$year*.csv -x clubs.$yday.csv *perf.$yday.csv
fi

# Get the educational achievements
PYTHONPATH=~/python:$PYTHONPATH ../geteducationals.py


# And exit
exit $ret
