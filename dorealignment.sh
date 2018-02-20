#!/bin/sh
# Even if we're running in a weird shell, let's use THIS directory as the current directory
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
data="$SCRIPTPATH/data"
cd "$data"   # Run in the data directory.
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/d101tm/lib/lib

# Make a subdirectory for all of the products of this run
mkdir alignment 2>/dev/null
export workfile=alignment/d101align.csv
echo createalignment
../createalignment.py --outfile $workfile
echo alignmap 
../alignmap.py --pindir pins --district 101 --testalign $workfile --makedivisions --outdir alignment
echo allstats
../allstats.py --outfile d101proforma.html --testalign $workfile --outdir alignment
echo makelocationreport
../makelocationreport.py --color --infile $workfile --outdir alignment
echo clubchanges
../clubchanges.py --from 3/15 --to 5/20 --outfile alignment/changes.html
echo makealignmentpage
../makealignmentpage.py > alignment/index.html

if [[ "block15" == $(hostname) || "ps590973" == $(hostname) ]] ; then
        echo "Copying to dailyalignment"
        cp alignment/* ~/files/dailyalignment/
fi
