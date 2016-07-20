#!/bin/bash

deactivate () {
    unset pydoc

    # reset old environment variables
    if [ -n "$_OLD_VIRTUAL_PATH" ] ; then
        PATH="$_OLD_VIRTUAL_PATH"
        export PATH
        unset _OLD_VIRTUAL_PATH
    fi
    if [ -n "$_OLD_VIRTUAL_PYTHONHOME" ] ; then
        PYTHONHOME="$_OLD_VIRTUAL_PYTHONHOME"
        export PYTHONHOME
        unset _OLD_VIRTUAL_PYTHONHOME
    fi

    # This should detect bash and zsh, which have a hash command that must
    # be called to get it to forget past commands.  Without forgetting
    # past commands the $PATH changes we made may not be respected
    if [ -n "$BASH" -o -n "$ZSH_VERSION" ] ; then
        hash -r 2>/dev/null
    fi

    if [ -n "$_OLD_VIRTUAL_PS1" ] ; then
        PS1="$_OLD_VIRTUAL_PS1"
        export PS1
        unset _OLD_VIRTUAL_PS1
    fi

    unset VIRTUAL_ENV
    if [ ! "$1" = "nondestructive" ] ; then
    # Self destruct!
        unset -f deactivate
    fi
}

cd data
rm latesttraining.html 2>/dev/null
../getfromdropbox.py --outfile latesttraining.html --cfile trainingcursor.txt --ext htm html --dir Training  || exit $?
echo $(date +"%B %e") | sed 's/  / /' > trainingreportdate.txt
export PYTHONPATH=~/python:$PYTHONPATH
/usr/bin/python ../training.py latesttraining.html --require9a || exit $?
exit
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
