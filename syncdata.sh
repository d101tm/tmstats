#!/bin/bash
rsync -vtzrL --exclude 'build' --exclude '*.yml' d101tm.org:src/tmstats/data/ ~/src/tmstats/data/
ssh d101tm.org 'mysqldump d101tm_tmstats | gzip' | gunzip | mysql d101tm_tmstats
ssh d101tm.org 'mysqldump d101tm_org | gzip' | gunzip | mysql d101tm_org
