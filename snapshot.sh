#!/bin/sh
echo 'copying from d4tm'
rsync -utzia --progress d4tm.org:bin/tmstats/data/ data/
echo 'running snapshot'
./snapshot.py || exit
echo 'copying snapshot to d4tm'
scp data/snapshot.* d4tm.org:www/files/stats/
echo 'clearing cache on d4tm'
ssh d4tm.org "bin/tmstats/clearcache.sh"

