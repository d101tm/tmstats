#!/bin/bash
. setup.sh

cd "$data"

echo "<p>Getting new roster</p>"
../getroster.sh
echo "<p>Processing Open House Report</p>"
echo "<p>Using roster file '$(cat rosterondropbox.txt)' from Dropbox</p>"

echo "<pre>"
../openhouse.py && isreal && cp openhouseclubs.html ~/files/reports/ && ../clearcache.py district-programs
echo "</pre>"
echo "<p>Open House Report has been updated on the <a href="/district-programs#openhousechallenge">District Programs</a> page.</p>"

