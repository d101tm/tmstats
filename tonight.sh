#!/bin/sh
cd data
if [ -e altdistrict.txt ] ; then
    echo "altdistrict exists" $(cat altdistrict.txt)
    ../createalignment.py 
else
    echo "No altdistrict"
    ../createalignment.py --trust
fi
../alignmap.py --pindir pins --district 101 --testalign d101align.csv  --nomakedivisions
../allstats.py --outfile d101proforma.html --newAlign d101align.csv
../makelocationreport.py --color --infile d101align.csv
../listclubsbycity.py  --newAlignment d101align.csv
../makealignmentpage.py > d101index.html
../build101areapage.py --outfile areapage.html --newAlignment d101align.csv

if [[ $? ]] ; then 
    if [[ "block15" == $(hostname) ]] ; then
        echo "Copying to alignment"
        cp d101proforma.html ~/files/alignment
        cp d101proforma.html ~/map
        cp d101newmarkers.js ~/files/alignment
        cp d101newmarkers.js ~/map
        cp d101location.html ~/files/alignment
        cp d101location.html ~/map
        cp d101index.html ~/files/alignment/index.html
        cp clublist.html ~/files/reports/clubs-by-city/index.html
        cp areapage.html ~/files/reports/areapage.html
    else
        echo "Copying to d101tm.org"
        scp d101proforma.html d101tm.org:files/alignment/
        scp d101newmarkers.js d101tm.org:files/alignment/
        scp d101location.html d101tm.org:files/alignment/
        scp d101index.html d101tm.org:files/alignment/index.html    
    fi

fi
