#!/bin/sh
./createalignment.py 
./alignmap.py --pindir /Users/david/src/map/pins --district 101 --testalign /Users/david/src/tmstats/data/d101align.csv  --nomakedivisions && (cd data;../allstats.py --outfile d101proforma.html --proforma d101align.csv)
(cd data;../makelocationreport.py --color --infile d101align.csv)
if [[ $? ]] ; then
    scp data/d101proforma.html d101tm.org:files/alignment/
    scp data/d101newmarkers.js d101tm.org:files/alignment/
    scp data/d101location.html d101tm.org:files/alignment/
fi
