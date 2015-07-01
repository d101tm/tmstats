#!/bin/bash
# This is the main driver for Toastmasters statistics.  It fetches the current files from Toastmasters and compares them
# to what we already have; if there's a change, it fires off the appropriate programs to do the major analysis.

# constants
dist=04
tmyear=2014-2015
lastyear=2013-2014

# Force Python to use UTF-8 for stdin and stdout and stderr throughout:
export PYTHONIOENCODING="utf8"

# Even if we're running in a weird shell, let's use THIS directory as the current directory
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
cd "$SCRIPTPATH"
data="$SCRIPTPATH/data"

if [ ! -d "$data" ] ; then
    mkdir ""$data""  
fi

# Keep track of where we started
savedir="$(pwd)"

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




# The very first thing to check is whether we have run successfully today.  
# If so, we're done.  
# Force a run by passing 'force' or 'test' as the first argument.
# 'test' will not zip and delete the historical CSVs.
if [ "x$1" != "xforce" -a "x$1" != "xtest" -a -e "$success" ] ; then
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


# Load the database
cd "$data"
echo "Loading database"
$savedir/loaddb.py 
cd "$savedir"

# Check for currency; if not, exit.
cd "$data"
$savedir/currency.py
rc=$?
if [[ "$rc" != 0 ]] ; then
    echo "return code: $rc, exiting"
    exit $rc
fi
cd "$savedir"




# Next, run the reformation report
echo "Running reformation analysis"

./reformation.py "$ymlfile"

rc=$?
if [[ "$rc" != 0 ]] ; then
   echo "return code: $rc, exiting"
   exit $rc
fi

# Next, run the statistics.  
echo "Running allstats"

cd "$data"
$savedir/allstats.py "$ymlfile"
cd "$savedir"

# Run March Madness
echo "Running March Madness"
./madness.py "$data/madness.html" "$ymlfile"

rc=$?
if [[ "$rc" != 0 ]] ; then
   echo "return code: $rc, exiting"
   exit $rc
fi

# Run Distinguished Clubs
echo "Running Distinguished Clubs"
./distclubs.py "$data/distclubs.html" "$ymlfile"

rc=$?
if [[ "$rc" != 0 ]] ; then
   echo "return code: $rc, exiting"
   exit $rc
fi

# Now, run the net gain report
echo "Running net gain report"
./nothinbutnet.py  "$data/net.html" "$data/net.css" "$ymlfile"

rc=$?
if [[ "$rc" != 0 ]] ; then
   echo "return code: $rc, exiting"
   exit $rc
fi

# And create a special version of the net gain report to be standalone, at least for testing

echo "<html><head><link rel='stylesheet' type='text/css' href='net.css'></head><body>" >$data/allnet.html
cat "$data/net.html" >> $data/allnet.html
echo "</body></html>" >> $data/allnet.html

# Now, create the clublisting
echo "Creating clubs by city"
cd "$data"
"$savedir"/listclubsbycity.py 
cd "$savedir"

rc=$?
if [[ "$rc" != 0 ]] ; then
   echo "return code: $rc, exiting"
   exit $rc
fi

# If we get this far, we win!
if [[ "x$1" == "xtest" ]] ; then
    echo "not deleting CSVs or recording success"
    exit $rc
fi

# Let's clean up earlier versions of the data files by consolidating them in the history ZIP file.  
# We leave yesterday's and today's intact.
cd "$data"
zip -Tm history clubperf.*.csv areaperf.*.csv clubs.*.csv distperf.*.csv clubchanges.*.eml -x \*.$today.\* -x \*.$yday.\*
rm *.success
cd "$savedir"
 
echo "Finished at $(date)" > "$success"
cat "$success"
