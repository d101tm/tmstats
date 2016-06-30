#!/bin/sh
cd data
../createalignment.py --alignment 2016-17D4.csv --outfile d4align.csv
../alignmap.py --pindir pins --district 4 --testalign d4align.csv  --nomakedivisions
