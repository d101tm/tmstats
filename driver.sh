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




# The very first thing to check is whether we have run successfully today.  If so, we're done.  Force a run by passing 'force' as the first argument.
if [ "x$1" != "xforce" -a -e "$success" ] ; then
    exit 2
fi

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

# Get historical data, if it doesn't already exist
if [ ! -a "$historical" ]; then
    curl -so "$historical" "http://dashboards.toastmasters.org/$lastyear/export.aspx?type=CSV&report=clubperformance~$dist~~~$lastyear"
fi

# Next thing is to see if Toastmasters has made their updates.  We'll get the performance reports for
#  District, Division/Area, and Clubs.  If any of them are unchanged, we stop and let the next cycle try again.

# District:

curl -so "$dtoday" "http://dashboards.toastmasters.org/export.aspx?type=CSV&report=districtperformance~$dist~~~$tmyear"
if cmp -s "$dtoday" "$dyday" ; then
    echo "No change in District Performance Report; exiting"
    exit 1
fi
    
# Division/Area:

curl -so "$atoday" "http://dashboards.toastmasters.org/export.aspx?type=CSV&report=divisionperformance~$dist~~~$tmyear"
if cmp -s "$atoday" "$ayday" ; then
    echo "No change in Area/Division Performance Report; exiting"
    exit 1
fi

# Club:

curl -so "$ctoday" "http://dashboards.toastmasters.org/export.aspx?type=CSV&report=clubperformance~$dist~~~$tmyear"
if cmp -s "$ctoday" "$cyday" ; then
    echo "No change in Club Performance Report; exiting"
    exit 1
fi

# OK, data has been updated.  We can proceed!
    
# Get the current club list.  (Updated for new TMI site)
curl -so $data/clubs.$today.csv  "https://www.toastmasters.org/api/club/exportclubs?format=text%2Fcsv&district=$dist"

# Check for changes, and if there are any, notify the Webmaster.
echo "Checking for club changes"

./clubchanges.py "$data/clubs.$today.csv" "$data/clubs.$yday.csv" > "$data/clubchanges.$today.eml"


# Next, run the reformation report
echo "Running reformation analysis"

./reformation.py "$ymlfile"

# Next, run the statistics.  The program is ill-behaved, so we need to move to the data directory first.
echo "Running allstats"

savedir="$(pwd)"
cd "$data"
$savedir/allstats.py "$ymlfile"
cd "$savedir"

# Now, run the net gain report
echo "Running net gain report"
./nothinbutnet.py  "$data/net.html" "$data/net.css" "$ymlfile"

# And create a special version of the net gain report to be standalone, at least for testing

echo "<html><head><link rel='stylesheet' type='text/css' href='net.css'></head><body>" >$data/allnet.html
cat "$data/net.html" >> $data/allnet.html
echo "</body></html>" >> $data/allnet.html

# Now, create the clublisting
./createlisting.py "$data/clubs.$today.csv"


# If we get this far, we win!
 
echo "Finished at $(date)" > "$success"
cat "$success"
