#!/bin/bash
# This is the main driver for Toastmasters statistics.  It fetches the current files from Toastmasters and compares them
# to what we already have; if there's a change, it fires off the appropriate programs to do the major analysis.

# constants
dist=04
tmyear=2014-2015
lastyear=2013-2014

# Even if we're running in a weird shell, let's use THIS directory as the current directory
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
cd "$SCRIPTPATH"
data="$SCRIPTPATH/data"
mkdir $data  # Just in case...
echo $data

# Life would be nice if we could always use the same commands.  We can't.  This should work on Mac OS X, Bluehost, and HostGator.
today=$(date +'%Y-%m-%d')
if ! yday=$(date -v-1d +'%Y-%m-%d' 2>/dev/null)
then
    yday=$(date -d '1 day ago' +'%Y-%m-%d' 2>/dev/null)
fi
echo $yday
    
# Start by getting the current club list.  It may not change every day, but in case it does, fire off the program to advise the
# webmaster of changes.

curl -so $data/clubs.$today.csv  "http://reports.toastmasters.org/findaclub/csvResults.cfm?District=$dist"
./clubchanges.py "$data/clubs.$today.csv" "$data/clubs.$yday.csv"