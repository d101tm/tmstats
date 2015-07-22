#!/bin/sh
# Reload the database.
cd data
foo=$(grep 'dbpass:' tmstats.yml);export dbpass=${foo##* }
foo=$(grep 'dbuser:' tmstats.yml);export dbuser=${foo##* }
foo=$(grep 'dbname:' tmstats.yml);export dbname=${foo##* }
cd ..
mysql --user=$dbuser --password=$dbpass $dbname <emptytables.sql
cd data
#unzip -n history.zip   
../loaddb.py -q

