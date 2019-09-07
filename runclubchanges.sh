#!/bin/bash
# Check for club changes, and if there are any, notify the Webmaster.
# Force python to use UTF-8 for stdin and stdout and stderr throughout:
export PYTHONIOENCODING="utf8"

. setup.sh

cd "$workdir"
outfile="clubchanges.$today.html"

if "$SCRIPTPATH/clubchanges.py" $* --outfile "$outfile"
then
    rm $outfile   # No changes noted
else 
    isreal && "$SCRIPTPATH/sendmail.py" --htmlfile "$outfile" --to  webmaster@d101tm.org growth@d101tm.org quality@d101tm.org dd@d101tm.org pr@d101tm.org --subject "Club Change Report for $today"
fi
