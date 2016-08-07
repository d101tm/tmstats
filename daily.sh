#!/bin/bash
# DreamHost setup for statistics.
export TZ=PST8PDT
#export PYTHONPATH="$HOME/python:$PYTHONPATH"

# Ensure we're in the right virtual environment
export VIRTUAL_ENV_DISABLE_PROMPT=1
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib
. ~/python2.7.11/bin/activate


# Even if we're running in a weird shell, let's use THIS directory as the current directory
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
data="$SCRIPTPATH/data"
cd "$data"   # Run in the data directory.

touch daily       # We were here!

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
   
    ### Run the allstats report
    if (( $haveboth == 0 )) ; then
        echo "running allstats"
        ../allstats.py 
        echo "allstats rc = $?"
    fi
    
    
    ### Run daily housekeeping
    if (( $haveclubs == 0 )) ; then
        
        echo "Running Club Change Report"
        ../runclubchanges.sh 
	
        echo "Running alignment-related"
        (cd ..;./tonight.sh)
    fi

        
    rm marker
    rm *.success 2>/dev/null
    
    echo "Finished at $(date)" > "$success"
    cat "$success"
fi    
