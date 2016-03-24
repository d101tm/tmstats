#!/bin/sh
./alignmap.py --pindir /Users/david/src/map/pins --district 101 --testalign /Users/david/src/tmstats/data/d101align.csv  --nomakedivisions && (cd data;../allstats.py --outfile d101proforma.html --proforma d101align.csv)
./alignmap.py --pindir /Users/david/src/map/pins --district 4 --testalign /Users/david/src/tmstats/data/d4align.csv  --nomakedivisions --outfile d4newmarkers.js && (cd data;../allstats.py --outfile d4proforma.html --proforma d4align.csv)
if [[ $? ]] ; then
    scp data/d101proforma.html d4tm.org:www/alignment/
    scp data/d101newmarkers.js d4tm.org:www/alignment/
    scp data/d4proforma.html d4tm.org:www/alignment/
    scp data/d4newmarkers.js d4tm.org:www/alignment/
    ssh d4tm.org bin/tmstats/clearcache.sh
fi
