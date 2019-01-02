#!/bin/bash
. setup.sh

cd "$data"

echo "<p>Getting new roster</p>"
../getroster.sh
echo "<p>Processing New Year's Challenge Report</p>"
echo "<p>Using roster file '$(cat rosterondropbox.txt)' from Dropbox</p>"

echo "<pre>"
../openhouse.py --outfile newyearschallenge.html --basedate 12/1 --finaldate 2/28 --renewto 9/30/2019 && isreal && cp newyearschallenge.html ~/files/reports/ 
src=$?
../clearcache.py district-programs
echo "</pre>"

if (( $src  == 0 )) ; then 
    echo "<p>New Year's Challenge Report has been updated on the <a href="/district-programs#newyearschallenge">District Programs</a> page.</p>"
elif isreal ; then
    echo "<p>Report not copied, rc=$src"
else
    echo "<p>Not on d101tm.org, so not copied."
fi

