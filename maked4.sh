#!/bin/sh
./alignmap.py --pindir /Users/david/src/map/pins --district 4 --testalign /Users/david/src/tmstats/data/d4align.csv  && (cd data;../allstats.py --outfile d4proforma.html --proforma d4align.csv)
exit
if [[ $? ]] ; then
    scp data/d101proforma.html d4tm.org:www/files/stats
    scp data/d101newmarkers.js d4tm.org:www/images/map
    ssh d4tm.org bin/tmstats/clearcache.sh
fi
