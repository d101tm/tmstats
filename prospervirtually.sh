#!/bin/bash
. setup.sh


echo "<p>Getting new roster</p>"
"$SCRIPTPATH"/getroster.sh
cd "$workdir"
echo "<p>Processing Prosper Virtually Report</p>"
echo "<p>Using roster file '$(cat rosterondropbox.txt)' from Dropbox</p>"

echo "<pre>"
"$SCRIPTPATH"/openhouse.py --renewto 3/31/2021 --sheetname "Prosper Virtually" --outfile "prospervirtuallyclubs.html" && isreal && cp prospervirtuallyclubs.html ~/files/reports/ 
src=$?
"$SCRIPTPATH"/clearcache.py district-programs
echo "</pre>"

if (( $src  == 0 )) ; then 
    echo "<p>Prosper Virtually Report has been updated on the <a href="/district-programs#prospervirtuallychallenge">District Programs</a> page.</p>"
elif isreal ; then
    echo "<p>Report not copied, rc=$src"
else
    echo "<p>Not on d101tm.org, so not copied."
fi

