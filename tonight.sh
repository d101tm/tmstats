#!/bin/sh
cd data
../createalignment.py 
../alignmap.py --pindir /Users/david/src/map/pins --district 101 --testalign d101align.csv  --nomakedivisions
../allstats.py --outfile d101proforma.html --proforma d101align.csv
../makelocationreport.py --color --infile d101align.csv
../makealignmentpage.py > d101index.html

if [[ $? ]] ; then 
    if [[ "block15" == $(hostname) ]] ; then
        echo "Copying to alignment"
        cp d101proforma.html ~/files/alignment
        cp d101newmarkers.js ~/files/alignment
        cp d101location.html ~/files/alignment
        cp d101index.html ~/files/alignment
    else
        echo "Copying to d101tm.org"
        scp d101proforma.html d101tm.org:files/alignment/
        scp d101newmarkers.js d101tm.org:files/alignment/
        scp d101location.html d101tm.org:files/alignment/
        scp d101index.html d101tm.org:files/alignment/index.html    
    fi

fi
