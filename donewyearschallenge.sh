#!/bin/bash
. setup.sh

echo "<p>Getting new roster</p>"
"$SCRIPTPATH"/getroster.sh
cd "$workdir"

echo "<p>Processing New Year's Challenge Report</p>"
echo "<p>Using roster file '$(cat rosterondropbox.txt)' from Dropbox</p>"

echo "<pre>"
"$SCRIPTPATH"/openhouse.py --outfile newyearschallenge.html --basedate 1/1 --finaldate 3/31 --renewto 9/30 --sheetname "2020 Winter" && isreal && cp newyearschallenge.html ~/files/reports/ 
src=$?
"$SCRIPTPATH"/clearcache.py district-programs
echo "</pre>"

if (( $src  == 0 )) ; then 
    echo "<p>New Year's Challenge Report has been updated on the <a href="/district-programs#newyearschallenge">District Programs</a> page.</p>"
elif isreal ; then
    echo "<p>Report not copied, rc=$src"
else
    echo "<p>Not on d101tm.org, so not copied."
fi

