#!/bin/bash
. setup.sh
cd "$workdir"
"$SCRIPTPATH"/listclubsbycity.py
"$SCRIPTPATH"/buildareapage.py --outfile areapage.html 
"$SCRIPTPATH"/makemap.py --outfile d101newmarkers.js


if [[ $? ]] && isreal ; then 
        echo "Copying map and reports"
        cp clublist.html ~/files/reports/clubs-by-city/index.html
        cp areapage.html ~/files/reports/areapage.html
        "$SCRIPTPATH"/clearcache.py divisions-and-areas
        cp d101newmarkers.js ~/map/
fi
