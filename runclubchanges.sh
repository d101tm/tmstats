#!/bin/bash
# Check for club changes, and if there are any, notify the Webmaster.
# Force python to use UTF-8 for stdin and stdout and stderr throughout:
export PYTHONIOENCODING="utf8"

. setup.sh

cd "$data"
outfile="clubchanges.$today.html"

if [ -n "$*" ] ; then
   runon="--runon $*"
else
   runon=""
fi

if "$SCRIPTPATH/clubchanges.py" $runon --outfile "$outfile"
then
    rm $outfile   # No changes noted
else 
    ifreal "$SCRIPTPATH/sendmail.py" --htmlfile "$outfile" --to mythili.toastmasters@gmail.com bina.toastmasters@gmail.com webmaster@d101tm.org growth@d101tm.org dd@d101tm.org katherine.toastmaster@gmail.com pr@d101tm.org --subject "Club Change Report for $today"
fi
