# Theory of Operation for TMSTATS

There are many programs and datasources used by the __tmstats__ suite.  This document explains them (or tries to explain them).

## Directory Structure ##

The programs should all be in one directory (I'll call it __tmstats__); data files for the programs, including the all-important [tmstats.yml][], belong in a subdirectory named __data__ of the tmstats directory.  The programs will chdir to the data subdirectory of the current directory if one exists; otherwise, they'll use the current directory as their __working directory__, so the driver script would need to ensure that the current directory is set to the data directory before invoking any of the programs.

Note that this means that any filenames on the command line or in the YMLfile are interpreted AFTER the program has changed to the proper directory!


## Driver Script

Each installation of the __tmstats__ suite needs its own driver script to adapt to local conditions (such as versions of Python and the eventual destination of the output files).  The driver script is for D101 Toastmasters on Dreamhost:

* dreamhost.sh (used by District 101 Toastmasters on Dreamhost)


### Basic Logic ###

The driver script is typically invoked from cron(1) once an hour.  Toastmasters typically posts new data by 7am Pacific Time, so the script exits immediatelly (unless forced to do so by a parameter) before 7am or after 11pm.  The scripts set TZ=PST8PDT to match Toastmasters' time.

The existing scripts accept one positional parameter, which can be one of:

| Parameter | Meaning |
| --------- | ------- |
| force     | run unconditionally; move daily data files into history.zip |
| test      | run unconditionally; don't move daily data files into history.zip |

If the parameter isn't specified, the script only runs between 7am and 11pm Pacific, and only if it hasn't run successfully that day.

If the script needs to run, it invokes [updateit.sh][] to fetch new data from Toastmasters and load it into the MySQL database specified in the YML file.  If updateit.sh is successful (as verifed by its exit status and [currency.py][], which makes sure that the database has current data for today), the driver script then invokes individual programs to create the various reports, maps, and other output files, and then copies those files to the places needed by the web server.  The driver script may also send email to the Webmaster or others to notify them of what happened - it's up to you!


### updateit.sh

This script is invoked by the driver script.  It has the same "force" and "test" parameters as the driver (which passes the parameters along), with the same meaning.

It creates variables $today and $yday (yesterday) with the appropriate dates in yyyy-mm-dd format.

If we already have today's club information and yesterday's performance information (I __should__ have tied club information to the previous day for consistency, but I didn't), we exit unless forced to continue.

[getperformancefiles.py][] is invoked to capture information from Toastmasters and put it into the appropriate CSV files.

Next, the script calls [loaddb.py][] to load the CSV files into the database.  Note that loaddb.py loads _all_ CSV files with the proper names (clubs._yyyy-mm-dd_.csv and *perf._yyyy-mm-dd_.csv) into the database, not just the most recent.

Next, the script calls [populatelastfor.py][] to update the "lastfor" table.  It normally only updates the current year's information, but if "force" was passed, it updates all years.

Unless the "test" option was passed, the script then zips all of the CSV files it used or created except for the most current.

Finally, the script invokes [geteducationals.py][] to update the educational achievements table.

The exit status from the script is 0 if all is well, or the sum of:

| value | meaning |
| ----: | ------- |
| 1     | loaddb.py made no changes to the database |
| 2     | unable to get club information from Toastmasters |
| 4     | unable to get performance information from Toastmasters |

## The Programs ##

Most of the programs are pretty straightforward; you can invoke any of them (unless otherwise noted) with "--help" to find out what parameters they accept.  I only explain the most important of the parameters in this document.  Almost all of them use the database.

I omit some of the simple shell scripts which manipulate things like the *tokens files.  I also omit most of the .sql files which declare tables.

### alignmap.py ###

This is a wrapper to [makemap.py][] which adds additional parameters and functions.  I will only describe the special parameters for this routine.

| Parameter | Value |
| --------- | ----- |
| --testalign | name of a ["test alignment" file][] |
| --makedivisions | if specified, the program computes division boundaries |
| --nomakedivisions | if specified, the program does not compute division boundaries |

By default, the program computes division boundaries for District 101, but not for District 4.  There are various hard-coded points in the program to adjust the District 101 boundaries to put Gilroy into Division A and to put Rancho San Antonio into Division B to make it contiguous.


### allstats.py ###

Creates the consolidated report file showing club, area, division, and district performance.  Uses the data in the database.

Specify "--proforma" with the name of a ["test alignment" file][] to create a pro-forma report for a possible new alignment.

### awardtallies.py ###

Creates CSV files with total "awards by division" and "awards by type".

### buildareapage.py ###

Builds an HTML fragment containing tables for the clubs in each area and the areas in each division.  Uses the ["officers" file][] specified in [tmstats.yml][].

### clubchanges.py ###

Create an HTML file with changes in club information between two dates, based on Toastmasters' Find-a-Club data.  There are up to three sections in the report:

* Clubs which are no longer in the list from Toastmasters
* Clubs which have been added to the list (with detailed infomation about each club)
* Clubs whose information has been changed (by default, only the area, division, place, address, and meeting information is checked or displayed.)

### codeit.py ###

Geocodes ALL current clubs in the clubs table and updates the GEO table.  You will usually redirect STDOUT to a file for reuse to avoid having to make too many queries to Google Maps in one day.

Probably no longer necessary; replaced by geocode.py.

### copywebfiles.py ###

Hacky program to copy files from the Webmaster Dropbox account's "D101 Web Files" directory to the local ~/files directory, creating subdirectories as needed.  

### createalignment.py ###

Uses a ["test alignment" file][] in Dropbox, the data in the database, and the ["map override" file][] to build a [consolidated CSV file][] with information from all clubs in the test alignment file (and only those clubs).  That file is used by [alignmap.py][], [allstats.py][], and [makelocationreport.py][] to create pro-forma reports and maps reflecting a possible alignment.

### currency.py ###

Check currency of all four tables for the date specified.
    
If no date is specified, we want the 'clubs' table to be current for today;
the other tables can be for today OR yesterday because they are one day behind on Toastmasters.

Return 0 if all four tables are current.    
Return 1 if only the clubs table is outdated.    
Return 2 in any other case.    
    
Uses the 'loaded' table.

### d101borders.py ###

Contains the borders of District 101.

### dbconn.py ###

Handles database connections for other programs.  

### dotraining.sh ###

Fetches the most current training report (using [gettrainingstatus.py][]); if it's changed, runs [training.py][] to create the necessary reports and then copies them to the appropriate directory (which is hard-coded).  This script is really for District 4 only.

### earlyachievers.py ###

Creates the "Early Achievers" report based on District 101's criteria.  The end date is a parameter, but nothing else is.

### emptytables.sql ###

Drops most of the tables.  Don't use it unless you are rebuilding everything.

### geocode.py ###

Wraps Google Maps geocoding functions for other programs.  If called as a stand-alone program, geocodes all clubs in the database.


### georeverse.py ###

Tries to compare our geocoding to that of WHQ and builds a report.  Not uses on a regular basis.  Not sure why I needed both this and [geocompare.py][] anymore!


### geteducationals.py ###

Parses the Toastmasters "Educational Achivements" page and updates the "awards" table.

### getperformancefiles.py ###

Gets performance (and club) data from Toastmasters.  Creates various CSV files with the information.  Uses the database to figure out what dates it needs to get data for, but does not update the database (that's done by [loaddb.py][]).

### getroster.py ###

Gets the latest roster file from the /roster directory in Dropbox and writes it as 'latestroster._ext_' (the extension matches that of the original, which can be XLS, XLSX, or CSV).  The Program Quality Director needs to save this file from District Central periodically; it is used to send congratulatory messages to members when they earn Educational Awards.

### gettrainingstatus.py ###

Gets the latest training status file from the /training directory in Dropbox and writes it as latesttraining.html.  The Program Quality Director has to save the status file when he or she updates the training status in District Central.

### grouper.py ###

Tries to create evenly-balanced Divisions based on geography and then divide them into equally-strong, fairly compact Areas.  Lots of special code for District 101, and, in the end, we only used the results of this program as a starting place for discussion.  No longer needed.

### ingestroster.py ###

Takes the roster file written by [getroster.py][] and puts it in the "roster" table in the database.

### latest.py ###

Gets the latest date in the database and the month for which it has data, based on the "loaded" table.  

### listclubsbycity.py ###

Creates an HTML file and fragments which list clubs by city.  

### loaddb.py ###

Takes the *perf.__date__.csv and clubs.__date__.csv files and puts them into the database.  Works around some problems with the Toastmasters "clubs" file.

### makealignmap.sh ###

No longer used.

### makealignmentpage.py ###

Creates an index.html page for the alignment directory on d101tm.org; mostly needed to put a time/date stamp on the page.

### makeapin.sh ###

Creates a pin for the map-by-area.  Creates the pin as "test.png", which is kind of silly.  Runs on a Mac, not the server.

### makecongrats.sh ###

Creates a page for the D4 promo cycle with the number of members who have earned awards.  Probably no longer needed (replaced by [makeeducationals.py][]).

### makeeducationals.py ###

Creates a page for the D4 promo cycle congratulating members who have recently earned Educational Awards.  Probably no longer needed.

### makelocationreport.py ###

Creates a report (based on a [consolidated CSV file][]) showing basic information for each club in a proposed Area and the greatest distance between any two clubs in the Area.

### makemap.py ###

Creates the club locator map.  [alignmap.py][] wrappers it.  

@@TODO@@ The two should be consolidated.


### overridepositions.py ###

Not a main program; used by several programs to update the club information with coordinates or locations from the ["map override" file].

### populatelastfor.py ###

Populates the "lastfor" table in the database, which many programs use to find the latest information available.

### presidentclub.py ###

Creates the HTML fragment for the "President's Club" award.


### punch12.py ###

Creates the HTML fragment for the "1-2 Punch" awards.

### reload.sh ###

Empties and reloads the entire database.  Don't use it.

### renewals.py ###

Generates the Stellar September and March Madness reports.

### resetdbto.py ###

Resets the database to its state on a specified date.  Used in testing.

### runclubchanges.sh ###

Runs the [clubchanges.py][] program to create a properly-named output file.

### sample.yml ###

A version of the [tmstats.yml][] file without any actual data.  Copy to your data directory, put in your data, and rename it.

### sanity.py ###

Creates the HTML fragment for the "September Sanity" award.

### sendawardmail.py ###

Creates and sends emails to members earning Educational Awards.  Uses the "roster" table and [awardmail.yml][].

### sendmail.py ###

Creates and sends mails (the content of the mail is in files whose names are parameters to this program).

### sharethewealth.py ###

Creats the HTML fragment for the "Share the Wealth" award.

### simpleclub.py ###

The class implementation used to maintain information about a club.  The name is historical.

### skeleton.py ###

A starting point for a new program in the suite.


### syncdata.sh ###

Copies information from D4TM to the local environment, including the database.  

### tmparms.py ###

The programs in the suite use this common [argparse](https://docs.python.org/2/library/argparse.html)-based argument parser to which they add any additional positional or keyword parameters they need.  The common parameters are:

| Parameter | Default | Meaning |
| --------- | ------- | ------- |
| --YMLfile | tmstats.yml | The filename of the master data file, normally [tmstats.yml][], relative to the working directory, which contains the default values for the environment |
| --dbname  | | For connection to MySQL |
| --dbhost  | localhost | For connection to MySQL |
| --dbuser  |  | For connection to MySQL |
| --dbpass  |  | For connection to MySQL (You should normally specify this in the YML file, not here)

The parser returns an object of type "tmparms" whose attributes correspond to the values read from the YML file, as overridden by paramaters defined by the program and specified when the program is invoked.

### tmutil.py ###

A collection of utility routines, used by many programs in the suite.  

@@TODO@@: Rewrite __overrideClubs__ to use the [consolidated CSV file][].

### training.py ###

Creates the training status report from the data saved by the Program Quality Director after updating training status.

### triplecrown.py ###

Creates the Triple Crown report HTML fragment using the District 4 definition (3 awards, at least one on the Communications track and at least one on the Leadership track).

### uncodeit.py ###

Rebuilds the "geo" table based on information originally captured by [codeit.py][].


## Use of Dropbox and Google Documents ##

Several programs in the suite use files which are held in Dropbox or as Google Documents (spreadsheets).

For Dropbox, each program uses a separate directory and maintains a pair of files, named "_something_state.txt" and "_something_tokens.txt" - the "tokens" file contains the application key and application secret for each program (as provided by the Dropbox developer dashboard).  The "state" file contains the oauth2 token (yes, this is confusingly named) which can either be provided from the dashboard or by explicitly logging in when you first run the program; it also contains a cursor from Dropbox reflecting the state of the last look at the directory.  These files are formatted as "key:value" lines; all of the programs which read them ignore lines they don't understand, so you could make them into proper YML files if you wanted.

For Google Documents, we use "security through obscurity"; you must use "publish to the web" to get the URL for each file, but there is no explicit authentication.
 
## Important data files ##


### tmstats.yml ###

Most of the information that differs between installations of __tmstats__ is held in a central control file (normally __tmstats.yml__).  This file is written using [YAML 1.1](http://yaml.org/spec/1.1/).  Some of the common values that programs expect to find here are:

| Key | Meaning |
| --- | ------- |
| district | The Toastmasters District for which the suite is being run |
| dbname | For connection to MySQL |
| dbhost | For connection to MySQL |
| dbuser | For connection to MySQL |
| dbpass | For connection to MySQL |
| officers | The URL of the CSV published form of the ["officers file"][] |
| newalignment | The filename of an XLSX file containing information about alignment to override that provided by Toastmasters.  Typically used at the beginning of a Toastmasters year.  (**TODO** change this to a Google spreadsheet) |
| googlemapsapikey | Used by the various mapping programs |
| makemap | Contains subkeys "mapoverride" and "pindir" |
| makemap.mapoverride | The URL of the CSV published form of a Google Spreadsheet with information about club meeting locations and times which is used in preference to that obtained from Toastmasters. |
| makemap.pindir | The filename of a directory containing pins for the maps (one pin for each possible Area) |

Note that filenames in the YML file are relative to the working directory (unless, of course, they are absolute filenames).

Programs MAY choose to allow values from the YML file to be overridden by defining them as parameters to the parser, but in most cases, the values in the YML file do not correspond to parameters to the programs.


### "test alignment" file ###

The "test alignment" file is a CSV file with the following columns (I only explain those that need it):

| Column | Value |
| ------ | ----- |
| newarea | new area, as A1 or C4 |
| clubnumber | |
| clubname | a comment - the value is ignored |
| color | Red (club under 12 members), Yellow (12-19 members), or Green (20 or more members) |
| likelytoclose | Enter "Yes" if the club is likely to close before the new year |
| latitude |
| longitude |
| place |
| address |
| city |
| state |
| zip |
| country |
| meetingday |
| meetingtime |

For those programs which use the test alignment file, only those clubs included in the file will be processed.  Clubs omitted from the file are silently dropped from the output.

All programs which use the test alignment file can use the [consolidated CSV file][] instead, except for [createalignment.py][].

### consolidated CSV file ###

This file is created by [createalignment.py][] and contains a merger of information from the Toastmasters database, as updated by the ["map override" file][] and the ["test alignment" file][].  Only clubs specifically listed in the test alignment file are included in this file.  Several programs use this file as their data source if told to do so.

### --newalignment ###

This is an Excel (.XLSX) file matching the format of the Toastmasters alignment file for 2015-16.  It should be replaced by the simpler ["test alignment" file][], but that hasn't happened yet.  The overrideClubs__ function in [tmutil.py][] processes this file.

### "officers" file ###

A Google spreadsheet containing the following columns:

Title, First, Last, Email, Notes

Title is of the form "Division _X_ Director" or "Area _Xn_ Director."

The Notes column is ignored by the programs using this file.

### awardmail.yml ###

Contains information needed to send mail in the local environment.  Used by [sendawardmail.py][].  Typical keys are mailserver, mailpw, mailport, from, and replyto.

### tmmail.yml ###

Contains information needed to send mail in the local environment.  Used by [sendmail.py][].  Typical keys are mailserver, mailpw, mailport, from, and replyto.

## Dependencies ##

### Google Docs API for Python ###

pip install --user --upgrade google-api-python-client

You must enable Google Sheets API from the Google Console and create an API token.
