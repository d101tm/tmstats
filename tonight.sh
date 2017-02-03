#!/bin/sh
cd data
../listclubsbycity.py
../build101areapage.py --outfile areapage.html 
../makemap.py --outfile d101newmarkers.js

if [[ $? ]] ; then 
    if [[ "block15" == $(hostname) ]] ; then
        echo "Copying map and reports"
        cp clublist.html ~/files/reports/clubs-by-city/index.html
        cp areapage.html ~/files/reports/areapage.html
        cp d101newmarkers.js ~/map/
    fi

fi
