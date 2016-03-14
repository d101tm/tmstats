#!/bin/sh
./alignmap.py --pindir /Users/david/src/map/pins --district 101 --testalign /Users/david/src/tmstats/data/d101align.csv  --makedivisions && (cd data;../allstats.py --outfile d101proforma.html --proforma d101align.csv)
if [[ $? ]] ; then
    scp data/d101proforma.html d4tm.org:www/files/stats
    scp data/d101newmarkers.js d4tm.org:www/images/map
    ssh d4tm.org bin/tmstats/clearcache.sh
fi
