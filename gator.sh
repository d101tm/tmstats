#!/bin/bash
# HostGator-specific setup for the tmstats environment
export TZ=PST8PDT
export PYTHONPATH="$HOME/python:$PYTHONPATH"

# Even if we're running in a weird shell, let's use THIS directory as the current directory
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
data="$SCRIPTPATH/data"
cd "$data"   # Run in the data directory.

touch hourly       # We were here!

export hour=$(date +'%k')
export xmd="x$(date +'%m%d')"
# We need to know today's date and yesterday's.
today=$(date +'%Y-%m-%d')
if ! yday=$(date -v-1d +'%Y-%m-%d' 2>/dev/null)
then
    yday=$(date -d '1 day ago' +'%Y-%m-%d' 2>/dev/null)
fi

# Name the file that shows if we've run successfully
success="$today.success"



#### OLD program setup section

# constants for old programs
dist=04
tmyear=2015-2016
lastyear=2014-2015

# Set up filenames
distperf="distperf"
areaperf="areaperf"
clubperf="clubperf"
historical="$lastyear.csv"
todaytail="$today.csv"
ydaytail="$yday.csv"
dtoday="$distperf.$todaytail"
dyday="$distperf.$ydaytail"
atoday="$areaperf.$todaytail"
ayday="$areaperf.$ydaytail"
ctoday="$clubperf.$todaytail"
cyday="$clubperf.$ydaytail"
clubstoday="clubs.$today.csv"
clubsyday="clubs.$yday.csv"
oldclubs="oldclubs.csv"
ymlfile="today.yml"

# Get historical data, if it doesn't already exist
if [ ! -a "$historical" ]; then
    curl -so "$historical" "http://dashboards.toastmasters.org/$lastyear/export.aspx?type=CSV&report=clubperformance~$dist~~~$lastyear"
fi


# Create the YML file with all of the filenames so that the old programs can run:

cat >"$ymlfile"  << EOF
%YAML 1.1
---
files:
    clubs:  $clubstoday
    payments: $dyday
    current: $cyday
    historical: $historical
    division: $ayday
EOF

#### END of OLD programs setup section

monthof() 
{
  themonth=$1
}


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

# Decide if there's any point in running the daily cycle.  If it's 
#   before 7am OR we've already successfully run today, don't do it
#   unless forced into the prospect

dorun="yes" 

if (( $hour < 7 )) ; then
    dorun="no"  # Don't run before 7 am
elif [ -e "$success" ] ; then
    dorun="no" # Don't run if we've run already today
fi 

if [[ "$force" = "force" ]] ; then
    # If it's a forced run, run!
    dorun="yes"
fi


if [[ "$dorun" = "yes" ]] ; then
    # Run the daily cycle
    ../updateit.sh "$*"
    let urc=$?
    let haveclubs=$(($urc & 4))  # 0 if we got them
    let haveperf=$(($urc & 2))   # 0 if we got the info
    let changed=$(($urc & 1))   # 0 if changes found
    let haveboth=$(($urc & 6))  # 0 if we have both sets
    
    echo "Updateit RC = $urc"

    
  
    if (( $changed != 0 )) && [[ "$force" = "" ]]    ; then
        # No changes detected and not forced, so just leave
        echo "Exiting - no changes"
        exit 2
    fi
    
    if (( $haveclubs != 0 )) ; then
        echo "Club information not received"
    fi
    
    if (( $haveperf != 0 )) ; then
        echo "Performance information not received"
    fi
    
    
    # Check for currency of data in the database.  If not, leave.
    ../currency.py
    rc=$?
    if [[ "$rc" != 0 ]] ; then
        echo "currency RC = $rc, exiting."
        exit $rc
    fi
    
    # Create the "marker" file that we use to figure out
    #    what files need to be copied to the server.
    touch marker
    
    # Figure out target directories
    if [ -d ~/www/files/stats ] ; then
        maindir=~/www/files/stats
    else
        maindir=""
    fi
    if [ -d ~/www/test/files/stats ] ; then
        testdir=~/www/test/files/stats
    else
        testdir=""
    fi


    sleep 1   # Make sure that the marker file has an older timestamp
   
    ### Run the allstats report  (TODO:  fix after updating the program)
    if (( $haveboth == 0 )) ; then
        echo "running allstats"
        ../allstats.py "$ymlfile"
        echo "allstats rc = $?"
    fi
    
    ### Run programs in support of District special offerings
    
    # Run March Madness (TODO: Add it)
    # Run Nothin' but Net (TODO: Add it)
    # Run Share the Wealth when the time comes
    
    if (( $haveperf == 0 )) ; then
        echo "Running Early Achievers"
        ../earlyachievers.py
    fi
    
    if (( $haveperf == 0 )) ; then
        echo "Running Smedley"
        ../smedley.py
    fi
    
    if (( $haveperf == 0 )) ; then
        echo "Running September Sanity"
        ../sanity.py
    fi
    
    ### Run daily housekeeping
    if (( $haveclubs == 0 )) ; then
        echo "Building Area/Division page"
        ../buildareapage.py
        # Creates areasanddivisions.html
        
        echo "Building Clubs by City page"
        ../listclubsbycity.py
        
        echo "Running Club Change Report"
        ../runclubchanges.sh Sat
        
    fi
    
    ## Now, copy files created in this process to the appropriate directories
    finder="find . -maxdepth 1 -mindepth 1 -newer marker"
    echo "Files to copy:"
    $finder | sort
    
    
    if [[ "$maindir" != "" ]] ; then
        echo "copying to $maindir"
        $finder -exec cp {} "$maindir" \;
        cp "clubs.$today.csv" "$maindir/clubs.csv"
        
    fi
    if [[ "$testdir" != "" ]] ; then
        echo "copying to $testdir"
        $finder -exec cp {} "$testdir" \;
        cp "clubs.$today.csv" "$testdir/clubs.csv"       
    fi
    
    rm marker
    rm *.success 2>/dev/null
    
    echo "Finished at $(date)" > "$success"
    cat "$success"
fi    
    
# Handle training reports and clear the cache, no matter what.
cd "$SCRIPTPATH/../training"
./doit.sh
cd "$SCRIPTPATH"
./clearcache.sh

# If voting is in process, handle the votes
#cd "$HOME/bin/tmvoting"
#./process.py council.yml
#./summarize.sh
#./nonvoters.sh

exit 0

        
	
