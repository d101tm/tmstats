#!/bin/bash
. setup.sh

cd data
# rm latesttraining.html 2>/dev/null
echo "No updates to the training report were found." > trainingmessage.txt
../getfromdropbox.py --outfile latesttraining.html --namefile trainingfileinfo.txt --cfile trainingcursor.txt --ext htm html --dir Training  || exit $?
echo $(date +"%B %e") | sed 's/  / /' > trainingreportdate.txt
../training.py latesttraining.html --bonus9a  || exit $?
export TARGET=$HOME/files/reports

if [ -d $TARGET ] ; then  
    for name in trainingreport*
    do
        isreal && cp $name $TARGET/${name/report/}
    done
    isreal && cp lucky7.html $TARGET/lucky7.html

    isreal && ../clearcache.py district-programs


    # Now, create the message to the Program Quality Director
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

The "Lucky 7" report is at http://files.d101tm.org/reports/lucky7.html  (it's an HTML fragment)
EOF

isreal && ../sendmail.py --textfile trainingmessage.txt --to quality@d101tm.org --bcc david@d2j.us --subject "$filemsg"

fi
