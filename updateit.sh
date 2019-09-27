#!/bin/bash
# This program fetches the latest statistics from Toastmasters and
#    adds them to the database.
# Return Code is the OR of these:
#   0:  all fine
#   1:  no changes detected (includes 'already run today without force')
#   2:  club info not received
#   4:  performance info not received

# We also get educational achievements but the return code is unaffected.



# Keep track of where we started
savedir="$(pwd)"


cd "$workdir"

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
$SCRIPTPATH/getperformancefiles.py

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
$SCRIPTPATH/loaddb.py
let ret=$ret+$?

# Update the lastfor table, normally for the last year, but if force, do all.
if [[ "$force" = "force" ]]
then
    $SCRIPTPATH/populatelastfor.py
else
    ../populatelastfor.py --latestonly
fi

# Move old files to history unless otherwise requested
if [[ "$zip" = "zip" ]]
then
    year=${yday:0:4}
    zip -mT ${archivedir}/hist$year.zip clubs.$year*.csv clubperf.$year*.csv areaperf.$year*.csv distperf.$year*.csv -x clubs.$yday.csv *perf.$yday.csv
fi

# Get the educational achievements
PYTHONPATH=~/python:$PYTHONPATH $SCRIPTPATH/geteducationals.py


# And exit
exit $ret
