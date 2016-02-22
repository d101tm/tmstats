#!/bin/sh
./alignmap.py --pindir /Users/david/src/map/pins --district 101 && open ../map/align.htm; (cd data;../allstats.py --proforma grouped.csv) && open data/stats.html
scp data/stats.html d4tm.org:www/files/stats/proforma101.html
scp data/newmarkers.js d4tm.org:www/images/map
ssh d4tm.org bin/tmstats/clearcache.sh