#!/bin/sh
export PYTHONPATH=~/python:$PYTHONPATH
cd data
rm latesttraining.html 2>/dev/null
echo $(date +"%B %e") | sed 's/  / /' > trainingreportdate.txt
../gettrainingstatus.py || exit $?
../training.py latesttraining.html --require9a || exit $?
if [ -d ~/www/files/training ] ; then  
    for name in trainingreport*
    do
        cp $name ~/www/files/training/${name##training}
    done
    cp lucky7.html ~/www/files/training/


    if [ -d ~/www/test/files/training ] ; then
        cp -p ~/www/files/training/*  ~/www/test/files/training/
    fi
    
    


    # Now, create the message to the Program Quality Directors
    if [ -e trainingfileinfo.txt ] ; then
        filets=" based on the data in $(cat trainingfileinfo.txt)"
    else
        filets=""
    fi
    filemsg="The training reports have been updated$filets"

    cat > trainingmessage.txt << EOF
${filemsg}.

See http://d4tm.org/files/training/report.html.
There is an Excel version of the report at http://d4tm.org/files/training/report.xlsx.

The "Lucky 7" report has also been updated on the "What's Trending" page.
EOF

    ../sendmail.py --textfile trainingmessage.txt --to quality@d4tm.org --bcc david@d2j.us --subject "$filemsg"

fi
