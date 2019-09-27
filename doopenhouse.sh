#!/bin/bash
. setup.sh

cd "$workdir"

echo "<p>Getting new roster</p>"
../getroster.sh
echo "<p>Processing Open House Report</p>"
echo "<p>Using roster file '$(cat rosterondropbox.txt)' from Dropbox</p>"

echo "<pre>"
../openhouse.py && isreal && cp openhouseclubs.html ~/files/reports/ 
src=$?
../clearcache.py district-programs
echo "</pre>"

if (( $src  == 0 )) ; then 
    echo "<p>Open House Report has been updated on the <a href="/district-programs#openhousechallenge">District Programs</a> page.</p>"
elif isreal ; then
    echo "<p>Report not copied, rc=$src"
else
    echo "<p>Not on d101tm.org, so not copied."
fi

