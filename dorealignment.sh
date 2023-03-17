#!/bin/bash
. setup.sh
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/d101tm/lib/lib

# Make a directory for all of the products of this run
mkdir "${alignmentdir}" 2>/dev/null
export workfile="${alignmentdir}/d101align.csv"

# Process parameters
if [[ "$*" =~ .*include.* ]]
then
    include=--include
else
    include=""
fi

if [[ "$*" =~ .*html.* ]]
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
"$SCRIPTPATH"/createalignment.py $include --outfile $workfile || exit 1
echo $ep
echo
echo Running alignmap 
echo $bp
"$SCRIPTPATH"/alignmap.py --pindir pins --district 101 --testalign $workfile --makedivisions --outdir "${alignmentdir}" || exit 2
echo $ep
echo
echo Running allstats
echo $bp
"$SCRIPTPATH"/allstats.py --outfile d101proforma.html --testalign $workfile --outdir "${alignmentdir}" --title "pro forma performance report" || exit 3
echo $ep
echo
echo Running makelocationreport with color
echo $bp
"$SCRIPTPATH"/makelocationreport.py --color --outfile d101details.html --infile $workfile --outdir "${alignmentdir}" || exit 4
echo $ep
echo
echo Running makelocationreport without color
echo $bp
"$SCRIPTPATH"/makelocationreport.py --infile $workfile --outfile d101location.html --outdir "${alignmentdir}" || exit 5
echo $ep
echo
echo Running clubchanges
echo $bp
"$SCRIPTPATH"/clubchanges.py --from $("$SCRIPTPATH"/getfirstdaywithdata.py) --outfile "${alignmentdir}"/changesthisyear.html
"$SCRIPTPATH"/clubchanges.py --from 3/17 --to 5/19 --outfile "${alignmentdir}"/changessincedecmeeting.html
echo $ep
echo
echo Running makealignmentpage
echo $bp
"$SCRIPTPATH"/makealignmentpage.py --fordec > "${alignmentdir}"/index.html
echo $ep
echo
if [[ "block15" == $(hostname) || "vps36552" == $(hostname) ]] ; then
        echo "Copying to workingalignment"
        mkdir ~/files/workingalignment 2>/dev/null
        cp -RH "${alignmentdir}"/* ~/files/workingalignment/
fi

if [[ "$*" =~ .*html.* ]]
then

cat << EOF
<p>Go to <a href="/files/workingalignment"/">http://d101tm.org/files/workingalignment</a> to see the results.
</p>
</body>
</html>
EOF
fi
