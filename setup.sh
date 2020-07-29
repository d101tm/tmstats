# Common setup for TMSTATS shell scripts - SOURCE this file.

if [[ $TMSTATS_SETUP != 1 ]]
then
    # DreamHost setup for statistics.
    export TZ=PST8PDT

    # Ensure we're in the right environment
    #export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib
    # Put Python 3.8 in the front
    export PATH="$HOME/opt/python-3.8/bin:$PATH"

    # Set environment variables
    # There are bugs in some versions of Bash that require the following ugly workaround
    source /dev/stdin <<< "$($HOME/src/tmstats/exportsettings.py)"
    export data="$workdir"  # For now

    export TMSTATS_SETUP=1

fi

cd "$SCRIPTPATH"       # Always move to this directory (no effect if not 'source'd, of course)

# Define helper functions

    isreal()
    {
        [[ $I_AM_D101TM == 1 ]]
    }

