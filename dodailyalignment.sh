#!/bin/sh
cd data
../listclubsbycity.py
../buildareapage.py --outfile areapage.html 
../makemap.py --outfile d101newmarkers.js

if [[ $? ]] ; then 
    if [[ "block15" == $(hostname) || "ps590973" == $(hostname) ]] ; then
        echo "Copying map and reports"
        cp clublist.html ~/files/reports/clubs-by-city/index.html
        cp areapage.html ~/files/reports/areapage.html
        ../clearcache.py divisions-and-areas
        cp d101newmarkers.js ~/map/
    fi

fi
