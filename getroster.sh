#!/bin/bash

# Ingest roster and process awards

cd $STATS_DATA
$STATS_HOME/getfromdropbox.py --outfile latestroster.+ --namefile rosterfilename.txt --cfile rostercursor.txt --dbfilenamefile rosterondropbox.txt --ext csv xls xlsx --dir roster  && $STATS_HOME/ingestroster.py $(cat rosterfilename.txt)
