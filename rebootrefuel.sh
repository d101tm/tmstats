#!/bin/bash
. setup.sh


echo "<p>Getting new roster</p>"
"$SCRIPTPATH"/getroster.sh
cd "$workdir"
echo "<p>Processing Reboot Refuel and Rebuild Report</p>"
echo "<p>Using roster file '$(cat rosterondropbox.txt)' from Dropbox</p>"

echo "<pre>"
"$SCRIPTPATH"/openhouse.py --renewto 9/30/2021 --sheetname "2021 Reboot Refuel Rebuild" --outfile "rebootrefuelclubs.html" && isreal && cp rebootrefuelclubs.html ~/files/reports/ 
src=$?
"$SCRIPTPATH"/clearcache.py district-programs
echo "</pre>"

if (( $src  == 0 )) ; then 
    echo "<p>Reboot Refuel and Rebuild Report has been updated on the <a href="/district-programs#openhousechallenge">District Programs</a> page.</p>"
elif isreal ; then
    echo "<p>Report not copied, rc=$src"
else
    echo "<p>Not on d101tm.org, so not copied."
fi

