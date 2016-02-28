#!/bin/bash
rsync -vtzr --exclude 'build' --exclude '*.yml' d4tm.org:bin/tmstats/data/ ~/src/tmstats/data/
ssh d4tm.org 'mysqldump d4tmadmn_tmstats | gzip' | gunzip | mysql d4tmadmn_tmstats
