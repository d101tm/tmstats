#!/bin/bash
. setup.sh

cd "$workdir"   # Run in the work directory.

touch hourly       # We were here!
# Handle training reports
cd "$SCRIPTPATH"
./dotraining101.sh

# Update contest and training pages
(cd "$workdir";$SCRIPTPATH/makecontestpage.py && isreal && cp contestschedule.html ~/files/reports/)
(cd "$workdir";$SCRIPTPATH/maketrainingpage.py && isreal && cp trainingschedule.html ~/files/reports/)

# Don't update open house results
#(cd "$workdir";$SCRIPTPATH/openhouse.py && isreal && cp openhouseclubs.html ~/files/reports/)

# Copy info from Dropbox
(cd "$workdir"; isreal && $SCRIPTPATH/copywebfiles.py)
