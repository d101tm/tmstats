#!/bin/bash
. setup.sh  # Do common setup

cd "$workdir"   # Run in the work directory.

touch daily       # We were here!



# Name the file that shows if we've run successfully
success="$today.success"


update="update"
if [ "$1" = "force" ]
then
    force="force"
    zip="zip"
elif [ "$1" = "test" ]
then
    force="force"
    zip=""
elif [ "$1" = "noupdate" ]
then
    update=""
    force="force"
    zip=""
else
    update="update"
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
    if [[ "$update" = "update" ]] ; then
        $SCRIPTPATH/updateit.sh "$*"
    else
        true  # Set return code to indicate success
    fi

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
    $SCRIPTPATH/currency.py
    rc=$?
    if [[ "$rc" != 0 ]] ; then
        echo "currency RC = $rc, exiting."
        exit $rc
    fi
    
    ### Run the allstats report
    if (( $haveboth == 0 )) ; then
        echo "running allstats"
        $SCRIPTPATH/allstats.py --outfile performance.html
        rc=$?
        echo "allstats rc = $rc"
        if [[ "$rc" == 0 ]] ; then
            isreal && cp performance.html ~/www/files/reports/
        fi

    fi
    
    if (( $haveperf == 0 )) ; then
        echo "Running award tallies"
        $SCRIPTPATH/awardtallies.py
        echo "Creating award files"
        month=$(date '+%m')
        year=$(date '+%Y')
        if [[ "$month" < "08" ]] ; then
            year=$(( $year - 1 ))
        fi
        # Python 3.7 passes a default locale to subprocesses that the
        # 'convert' command doesn't like, so override it with
        # LC_ALL=C in the invocation of makeeducationals.
        LC_ALL=C $SCRIPTPATH/makeeducationals.py --since "$year-07-01"
        rc=$?
        echo "makeeducationals rc = $rc"
        if [[ "$rc" == 0 ]] ; then
            isreal && cp recentawards.* ~/www/files/reports
        fi
        # convert "recentawards.jpg" -resize 100x65 "100x65_recentawards.jpg"

        # Run renewals when appropriate
        # Stellar September starts with August data and continues through September 15
        if $SCRIPTPATH/require.py --newtmyear --datafor S8 --nodatafor 9/16 ; then
            echo "Running Stellar September"
            $SCRIPTPATH/stellar.py --program "stellar" --pct 75 100 --earn 75 100 && isreal && cp stellar.* ~/www/files/reports
        fi

        # March Madness starts with February data and continues through March 15
        if $SCRIPTPATH/require.py --datafor S2 --nodatafor 3/16 ; then
            echo "Running March Madness"
            $SCRIPTPATH/renewals.py --program "madness" --pct 75 90 100 --earn 50 75 101 && isreal && cp madness.* ~/www/files/reports
        fi

        # President's Club runs once we have February data and stops when we have April 16 data
        if $SCRIPTPATH/require.py --datafor S2 --nodatafor 4/16 ; then
            echo "Running President's Club"
            $SCRIPTPATH/presidentsclub.py && isreal && cp presidentsclub.txt ~/www/files/reports/
        fi

        # Early Achievers starts when we have data for the new year and ends when we have November data
        if $SCRIPTPATH/require.py --newtmyear --nodatafor S11 ; then
            echo "Running Early Achievers"
            $SCRIPTPATH/earlyachievers.py && isreal && cp earlyachievers.* ~/www/files/reports/
        fi
        
        # Take a Leap runs once we have April data and stops when we have data for the next year
        if false && $SCRIPTPATH/require.py --datafor S4 --oldtmyear ; then
            echo "Running Take A Leap"
            $SCRIPTPATH/takealeap.py && isreal && cp takealeap.* ~/www/files/reports/
        fi

        # Spring Forward runs once we have April data and stops when we have data for the next year
        if false && $SCRIPTPATH/require.py --datafor S5 --oldtmyear ; then
            echo "Running Spring Forward"
            $SCRIPTPATH/springforward.py && isreal && cp springforward.* ~/www/files/reports
        fi

        # Sensational Summer runs once we have April data and stops when we have data for the next year
        if $SCRIPTPATH/require.py --datafor S5 --oldtmyear ; then
            echo "Running Sensational Summer"
            $SCRIPTPATH/summer.py && isreal && cp summer.* ~/www/files/reports
        fi

        # Five for 5 runs once we have April data and stops when we get data for 5/16.
        if false && $SCRIPTPATH/require.py --datafor S4 --nodatafor 5/16; then
            echo "Running Five for 5"
            $SCRIPTPATH/fivefor5.py && isreal && (cp fivefor5.html ~/www/files/reports; $SCRIPTPATH/sendmail.py --subject "Five for 5 Report" --to quality@d101tm.org --html fivefor5.email)
        fi

    fi
    
    ### During alignment season, run the daily alignment report
    if $SCRIPTPATH/require.py --between 2/1 5/11; then
        echo "Running realignment programs"
        (cd $SCRIPTPATH;./dorealignment.sh > /dev/null)
    fi

    ### Run daily housekeeping
    if (( $haveclubs == 0 )) ; then
        
        echo "Running Club Change Report"
        (cd $SCRIPTPATH;./runclubchanges.sh) 
	
        echo "Running alignment-related"
        (cd $SCRIPTPATH;./dodailyalignment.sh)
		
		echo "Creating anniversary table"
		(cd $SCRIPTPATH/;./makeanniversarytable.py) && isreal && cp anniversary.csv ~/www/files/reports
    fi

    echo "Updating anniversary open houses"
    (cd $SCRIPTPATH/;./updateanniversaryopenhouses.py)

    # Now, ingest rosters if need be
    echo "Checking for a new roster"
    (cd $SCRIPTPATH/;./getroster.sh)

    # And process award letters
    if isreal
        then
            echo "Processing award letters"
            (cd $SCRIPTPATH;./sendawardmail.py)
    else
            echo "Processing award letters as a dry run"
            (cd $SCRIPTPATH;./sendawardmail.py --dryrun)
    fi

    # Make exportable copy of the database
    isreal && $SCRIPTPATH/exportdb.sh
        
    rm *.success 2>/dev/null

    isreal && $SCRIPTPATH/clearcache.py --all
    
    echo "Finished at $(date)" > "$success"
    cat "$success"
fi    
