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

if [ ! -d "$data" ] ; then
    mkdir ""$data""  
fi

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
historical="$data/$lastyear.csv"
todaytail="$today.csv"
ydaytail="$yday.csv"
dtoday="$distperf.$todaytail"
dyday="$distperf.$ydaytail"
atoday="$areaperf.$todaytail"
ayday="$areaperf.$ydaytail"
ctoday="$clubperf.$todaytail"
cyday="$clubperf.$ydaytail"
clubstoday="$data/clubs.$today.csv"
clubsyday="$data/clubs.$yday.csv"
oldclubs="$data/oldclubs.csv"
ymlfile="$data/today.yml"

# Create the YML file with all of the filenames so that the other programs can run:
cat >"$ymlfile"  << EOF
%YAML 1.1
---
files:
    clubs:  $clubstoday
    payments: $dtoday
    current: $ctoday
    historical: $historical
    division: $atoday
EOF


# The very first thing to check is whether we have run successfully today.  If so, we're done.
if [ -a "$success" ]; then
    exit 0
fi

# Get historical data, if it doesn't already exist
if [ ! -a "$historical" ]; then
    curl -so "$historical" "http://dashboards.toastmasters.org/$lastyear/export.aspx?type=CSV&report=clubperformance~$dist~~~$lastyear"
fi

# Next thing is to see if Toastmasters has made their updates.  We'll get the performance reports for
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

./clubchanges.py "$data/clubs.$today.csv" "$data/clubs.$yday.csv" > "$data/clubchanges.$today.eml"


# Next, run the reformation report

./reformation.py "$ymlfile"

# Next, run the statistics.  The program is ill-behaved, so we need to move to the data directory first.

savedir="$(pwd)"
cd "$data"
$savedir/allstats.py "$ymlfile"
 
 
