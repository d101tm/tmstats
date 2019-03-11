#!/bin/bash
# Make a clean (exportable) copy of the TMSTATS database
echo "Dumping TMSTATS"
mysqldump d101tm_tmstats | gzip > ~/files/exports/tmstats.sql.gz
echo "Dumping WordPress"
mysqldump d101tm_org | gzip > ~/files/exports/wp.sql.gz
