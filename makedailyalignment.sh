#!/bin/sh
export LIB=$LIB:/home/d101tm/lib/lib
../createalignment.py
../alignmap.py --pindir pins --district 101 --testalign d101align.csv --makedivisions
../allstats.py --outfile d101proforma.html --newAlign d101align.csv
../makelocationreport.py --infile d101align.csv
../makealignmentpage.py > d101index.html

if [[ "block15" == $(hostname) ]] ; then
        echo "Copying to dailyalignment"
        cp d101proforma.html ~/files/dailyalignment
        cp d101newmarkers.js ~/files/dailyalignment
        cp d101location.html ~/files/dailyalignment
        cp d101minimal.html ~/files/dailyalignment
        cp d101migration.html ~/files/dailyalignment
        cp d101index.html ~/files/dailyalignment/index.html

fi
