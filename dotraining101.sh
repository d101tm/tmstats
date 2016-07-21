#!/bin/bash


cd data
rm latesttraining.html 2>/dev/null
../getfromdropbox.py --outfile latesttraining.html --cfile trainingcursor.txt --ext htm html --dir Training  || exit $?
echo $(date +"%B %e") | sed 's/  / /' > trainingreportdate.txt
../training.py latesttraining.html || exit $?
export TARGET=$HOME/files/reports

if [ -d $TARGET ] ; then  
    for name in trainingreport*
    do
        cp $name $TARGET/${name/report/}
    done
    cp lucky7.html $TARGET/lucky7.table



    # Now, create the message to the Program Quality Directors
    if [ -e trainingfileinfo.txt ] ; then
        filets=" based on the data in $(cat trainingfileinfo.txt)"
    else
        filets=""
    fi
    filemsg="The training reports have been updated$filets"

    cat > trainingmessage.txt << EOF
${filemsg}.

See http://files.d101tm.org/reports/training.html
There is an Excel version of the report at http://files.d101tm.org/reports/training.xlsx

The "Lucky 7" report has also been updated on the "What's Trending" page.
EOF

echo    ../sendmail.py --textfile trainingmessage.txt --to quality@d101tm.org --bcc david@d2j.us --subject "$filemsg"

fi
