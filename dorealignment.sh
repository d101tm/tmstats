#!/bin/bash
. setup.sh
cd "$data"   # Run in the data directory.
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/d101tm/lib/lib

# Make a subdirectory for all of the products of this run
mkdir alignment 2>/dev/null
export workfile=alignment/d101align.csv

if [ "$1" = "html" ]
then
cat << EOF
Content-Type: text/html; charset=utf-8

<html>
<head><title>Running Alignment Programs</title></head>
<body>
EOF
bp="<pre>"
ep="</pre>"
else
bp=""
ep=""
fi

echo 'Running createalignment'
echo $bp
../createalignment.py --outfile $workfile || exit 1
echo $ep
echo
echo Running alignmap 
echo $bp
../alignmap.py --pindir pins --district 101 --testalign $workfile --makedivisions --outdir alignment || exit 2
echo $ep
echo
echo Running allstats
echo $bp
../allstats.py --outfile d101proforma.html --testalign $workfile --outdir alignment --title "pro forma performance report" || exit 3
echo $ep
echo
echo Running makelocationreport with color
echo $bp
../makelocationreport.py --color --outfile d101details.html --infile $workfile --outdir alignment || exit 4
echo $ep
echo
echo Running makelocationreport without color
echo $bp
../makelocationreport.py --infile $workfile --outdir alignment || exit 5
echo $ep
echo
echo Running clubchanges
echo $bp
../clubchanges.py --from $(../getfirstdaywithdata.py) --outfile alignment/changesthisyear.html
../clubchanges.py --from 3/17 --to 5/19 --outfile alignment/changessincedecmeeting.html
echo $ep
echo
echo Running makealignmentpage
echo $bp
../makealignmentpage.py > alignment/index.html
echo $ep
echo
if [[ "block15" == $(hostname) || "ps590973" == $(hostname) ]] ; then
        echo "Copying to workingalignment"
        mkdir ~/files/workingalignment 2>/dev/null
        cp alignment/* ~/files/workingalignment/
fi

if [ "$1" = "html" ]
then

cat << EOF
<p>Go to <a href="/files/workingalignment/">http://d101tm.org/files/workingalignment</a> to see the results.
</p>
</body>
</html>
EOF
fi
