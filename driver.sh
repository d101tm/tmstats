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

# Set up filenames
success="$data/$today.success"
distperf="$data/distperf"
areaperf="$data/areaperf"
clubperf="$data/clubperf"
historical="$data/historical"
todaytail="$today.csv"
ydaytail="$yday.csv"
dtoday="$distperf.$todaytail"
dyday="$distperf.$ydaytail"
atoday="$areaperf.$todaytail"
ayday="$areaperf.$ydaytail"
ctoday="$clubperf.$todaytail"
cyday="$clubperf.$ydaytail"


# The very first thing to check is whether we have run successfully today.  If so, we're done.
if [ -a "$success" ]; then
    exit 0
fi

# Nope.  Next thing is to see if Toastmasters has made their updates.  We'll get the performance reports for
#  District, Division/Area, and Clubs.  If any of them are unchanged, we stop and let the next cycle try again.

# District:

curl -so "$dtoday" "http://dashboards.toastmasters.org/export.aspx?type=CSV&report=districtperformance~$dist~~~$tmyear"
if [  ! -e "$dyday" ] && cmp -s "$dtoday" "$dyday" ; then
    exit 0
fi
    
# Division/Area:

curl -so "$atoday" "http://dashboards.toastmasters.org/export.aspx?type=CSV&report=divisionperformance~$dist~~~$tmyear"
if [  ! -e "$ayday" ] && cmp -s "$atoday" "$ayday" ; then
    exit 0
fi

# Club:

curl -so "$ctoday" "http://dashboards.toastmasters.org/export.aspx?type=CSV&report=clubperformance~$dist~~~$tmyear"
if [  ! -e "$cyday" ] && cmp -s "$ctoday" "$cyday" ; then
    exit 0
fi

# OK, data has been updated.  We can proceed!
    
# Get the current club list.  

curl -so $data/clubs.$today.csv  "http://reports.toastmasters.org/findaclub/csvResults.cfm?District=$dist"

# Check for changes, and if there are any, notify the Webmaster.

./clubchanges.py "$data/clubs.$today.csv" "$data/clubs.$yday.csv"

