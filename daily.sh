#!/bin/bash
. setup.sh  # Do common setup

cd "$data"   # Run in the data directory.

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
        ../updateit.sh "$*"
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
    ../currency.py
    rc=$?
    if [[ "$rc" != 0 ]] ; then
        echo "currency RC = $rc, exiting."
        exit $rc
    fi
    
    # Create the "marker" file that we use to figure out
    #    what files need to be copied to the server.
    touch marker


    sleep 1   # Make sure that the marker file has an older timestamp
   
    ### Run the allstats report
    if (( $haveboth == 0 )) ; then
        echo "running allstats"
        ../allstats.py --outfile performance.html
        rc=$?
        echo "allstats rc = $rc"
        if [[ "$rc" == 0 ]] ; then
            isreal && cp performance.html ~/www/files/reports/
        fi

    fi
    
    if (( $haveperf == 0 )) ; then
        echo "Running award tallies"
        ../awardtallies.py
        echo "Creating award files"
        month=$(date '+%m')
        year=$(date '+%Y')
        if [[ "$month" < "08" ]] ; then
            year=$(( $year - 1 ))
        fi
        # Python 3.7 passes a default locale to subprocesses that the
        # 'convert' command doesn't like, so override it with
        # LC_ALL=C in the invocation of makeeducationals.
        LC_ALL=C ../makeeducationals.py --since "$year-07-01"
        rc=$?
        echo "makeeducationals rc = $rc"
        if [[ "$rc" == 0 ]] ; then
            isreal && cp recentawards.* ~/www/files/reports
        fi
        # convert "recentawards.jpg" -resize 100x65 "100x65_recentawards.jpg"

        # Run renewals when appropriate
        # Stellar September starts with August data and continues through September 15
        if ../require.py --newtmyear --datafor S8 --nodatafor 9/16 ; then
            echo "Running Stellar September"
            ../renewals.py --program "stellar" --pct 75 90 100 --earn 50 75 101 --name '' '' 'Gold Club' && isreal && cp stellar.* ~/www/files/reports
        fi

        # March Madness starts with February data and continues through March 15
        if ../require.py --datafor S2 --nodatafor 3/16 ; then
            echo "Running March Madness"
            ../renewals.py --program "madness" --pct 75 90 100 --earn 50 75 101 && isreal && cp madness.* ~/www/files/reports
        fi

        # President's Club runs once we have March data and stops when we have April 16 data
        if ../require.py --datafor S3 --nodatafor 4/16 ; then
            echo "Running President's Club"
            ../presidentsclub.py && isreal && cp presidentsclub.txt ~/www/files/reports/
        fi

        # Early Achievers starts when we have data for the new year and ends when we have November data
        if ../require.py --newtmyear --nodatafor S11 ; then
            echo "Running Early Achievers"
            ../earlyachievers.py && isreal && cp earlyachievers.* ~/www/files/reports/
        fi
        
        # Take a Leap runs once we have April data and stops when we have data for the next year
        if false && ../require.py --datafor S4 --oldtmyear ; then
            echo "Running Take A Leap"
            ../takealeap.py && isreal && cp takealeap.* ~/www/files/reports/
        fi

        # Spring Forward runs once we have April data and stops when we have data for the next year
        if ../require.py --datafor S5 --oldtmyear ; then
            echo "Running Spring Forward"
            ../springforward.py && isreal && cp springforward.* ~/www/files/reports
        fi

        # Five for 5 runs once we have April data and stops when we get data for 5/16.
        if false && ../require.py --datafor S4 --nodatafor 5/16; then
            echo "Running Five for 5"
            ../fivefor5.py && isreal && (cp fivefor5.html ~/www/files/reports; ../sendmail.py --subject "Five for 5 Report" --to quality@d101tm.org --html fivefor5.email)
        fi

    fi
    
    ### During alignment season, run the daily alignment report
    if ../require.py --between 2/1 5/20; then
        echo "Running realignment programs"
        ../dorealignment.sh > /dev/null
    fi

    ### Run daily housekeeping
    if (( $haveclubs == 0 )) ; then
        
        echo "Running Club Change Report"
        (cd ..;./runclubchanges.sh) 
	
        echo "Running alignment-related"
        (cd ..;./dodailyalignment.sh)
		
		echo "Creating anniversary table"
		(cd ../;./makeanniversarytable.py) && isreal && cp anniversary.csv ~/www/files/reports
    fi


    # Now, ingest rosters if need be
    echo "Checking for a new roster"
    ../getroster.sh

    # And process award letters
    if [[ $I_AM_D101TM == 1 ]]
        then
            echo "Processing award letters"
            ../sendawardmail.py
    else
            echo "Processing award letters as a dry run"
	    ../sendawardmail.py --dryrun
    fi
        
    rm marker
    rm *.success 2>/dev/null

    isreal && ../clearcache.py --all
    
    echo "Finished at $(date)" > "$success"
    cat "$success"
fi    
