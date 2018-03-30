#!/bin/bash

. setup.sh

cd "$data"   # Run in the data directory.

touch hourly       # We were here!
# Handle training reports
cd "$SCRIPTPATH"
./dotraining101.sh

# Update contest and training pages
(cd data;../makecontestpage.py && ifreal cp contestschedule.html ~/files/reports/)
(cd data;../maketrainingpage.py && ifreal cp trainingschedule.html ~/files/reports/)

# Don't update open house results
#(cd data;../openhouse.py && cp openhouseclubs.html ~/files/reports/)

# Copy info from Dropbox
(cd data; ifreal ../copywebfiles.py)
