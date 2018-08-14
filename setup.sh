# Common setup for TMSTATS shell scripts - SOURCE this file.

if [[ $TMSTATS_SETUP != 1 ]]
then
    # DreamHost setup for statistics.
    export TZ=PST8PDT
    #export PYTHONPATH="$HOME/python:$PYTHONPATH"

    # Ensure we're in the right environment
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib
    # Put Python 3.7 in the front
    export PATH="$HOME/opt/python-3.7.0/bin:$PATH"


    # Even if we're running in a weird shell, let's use THIS directory as the current directory
    export SCRIPTPATH="$( cd "$(dirname -- "$0")" ; pwd -P )"
    export data="$SCRIPTPATH/data"

    export STATS_HOME="$SCRIPTPATH"
    export STATS_DATA="$STATS_HOME/data"
    
    export hour=$(date +'%k')
    export xmd="x$(date +'%m%d')"
    # We need to know today's date and yesterday's.
    export today=$(date +'%Y-%m-%d')
    
    # Work with GNU date or regular POSIX date command
    if ! yday=$(date -v-1d +'%Y-%m-%d' 2>/dev/null)
    then
        yday=$(date -d '1 day ago' +'%Y-%m-%d' 2>/dev/null)
    fi
    export yday


    export TMSTATS_SETUP=1

fi

# Define helper functions

    isreal()
    {
        [[ $I_AM_D101TM == 1 ]]
    }

