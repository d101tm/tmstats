#!/bin/bash
. setup.sh
# Reload the database.
foo=$(grep 'dbpass:' tmstats.ini);export dbpass=${foo##* }
foo=$(grep 'dbuser:' tmstats.ini);export dbuser=${foo##* }
foo=$(grep 'dbname:' tmstats.ini);export dbname=${foo##* }
echo mysql --user=$dbuser --password=$dbpass $dbname <emptytables.sql
cd "$archivedir"
mkdir "$workdir/csvdir"
cd "$workdir/csvdir"
for i in "$archivedir/hist*zip" 
do
    unzip "$i"
done
echo "$SCRIPTPATH"/loaddb.py -q

