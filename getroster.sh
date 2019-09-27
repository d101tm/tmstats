#!/bin/bash
# Fetch latest roster from Dropbox and ingest into database

. setup.sh
cd $workdir
$SCRIPTPATH/getfromdropbox.py --outfile latestroster.+ --namefile rosterfilename.txt --cfile ${cursordir}/rostercursor.txt --dbfilenamefile rosterondropbox.txt --ext csv  --dir roster  && $SCRIPTPATH/ingestroster.py $(cat rosterfilename.txt)
