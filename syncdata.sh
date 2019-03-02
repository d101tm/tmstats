#!/bin/bash
rsync -vtzrL --exclude 'build' --exclude '*.yml' d101tm.org:src/tmstats/data/ ~/src/tmstats/data/
echo "Loading TMSTATS"
curl "https://d101tm.org/files/exports/tmstats.sql.gz" | gunzip | mysql d101tm_tmstats
echo "Loading WordPress"
ssh d101tm.org 'mysqldump d101tm_org | gzip' | gunzip | mysql d101tm_org
