#!/usr/bin/env python

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.

import dbconn, tmutil, sys, os, csv


def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print >> file, ' '.join(args)

### Insert classes and functions here.  The main program begins in the "if" statement below.

def openarea(outfile, area):
    outfile.write('<div class="area">\n')
    outfile.write('<h4>Area %s</h4>\n' % area)
    outfile.write('<table class="areatable">\n')
    outfile.write('<thead>\n')
    outfile.write('<tr>\n')
    outfile.write('<th class="cnum">Number</th><th class="cname">Name</th><th class="color">Color</th><th class="members">Members</th><th class="goals">Goals</th><th class="loc">Location</th><th class="mtg">Time</th>\n')
    outfile.write('</tr>\n')
    outfile.write('</thead><tbody>\n')
    
def closearea(outfile):
    outfile.write('</tbody></table>\n')
    outfile.write('</div>\n')
    
def opendiv(outfile, division):
    outfile.write('<div class="division"><h3>Division %s</h3>\n' % division)
    
def closediv(outfile):
    outfile.write('</div>\n')

if __name__ == "__main__":
 
    import tmparms
    from tmutil import gotodatadir
    # Make it easy to run under TextMate
    gotodatadir()
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--infile', default='d101align.csv')
    parms.add_argument('--outfile', default='d101location.html')
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Your main program begins here.
    # Simple and ugly program to create location/time realignment listings
    outfile = open(parms.outfile, 'w')
    outfile.write("""
    <html>
    <head>
    <style type="text/css">
    
    
     body {font-family: Arial }
    

    .area {margin-bottom: 12pt; width: 100%; page-break-inside: avoid; display: block;}

    .division {border: none; break-before: always !important; display: block; float: none; position: relative; page-break-inside: avoid; page-break-after: always !important;}
      .areatable {font-size: 10pt; border: 1px solid black; border-collapse: collapse;}
      .myrow td {vertical-align: top; padding-left: 3px; padding-right: 3px; border: 1px solid black;}
      th {font-weight: bold; border: 1px solid black; border-collaps: collapse;}
      .ghost {background-color: #C0C0C0;}
      .myrow {border: 1px solid black; border-collapse: collapse;}
      .cnum {text-align: right; width: 7%;}
      .cname {text-align: left; width: 15%;}
      .color {text-align: left; width: 5%;}
      .red {background-color: red;}
      .yellow {background-color: yellow;}
      .green {background-color: green;}
      .goals {text-align: right; width: 5%;}
      .members {text-align: right; width: 5%;}
      .mtg {text-align: left; width: 25%;}
      .loc {text-align: left; width: 30%;}
    </style>
    </head>
    <body>
    """)
    reader = csv.DictReader(open(parms.infile, 'rbU'))
    thisdiv = ''
    thisarea = ''
    for row in reader:
        area = row['newarea']
        div = area[0]
        if thisarea and thisarea != area:
            closearea(outfile)
        if thisdiv and thisdiv != div:
            closediv(outfile)
        if thisdiv != div:
            opendiv(outfile, div)
        if thisarea != area:
            openarea(outfile, area)
        thisarea = area
        thisdiv = div
        outrow = []
        row['closing'] = '<br />(Probably closing)' if row['likelytoclose'] else ''
        outrow.append('<tr class="myrow%s">' % (' ghost' if row['likelytoclose'] else ''))
        outrow.append('  <td class="cnum">{clubnumber}</td><td class="cname">{clubname}{closing}</td>')
        outrow.append('  <td class="color {color}">{color}</td>\n')
        outrow.append('  <td class="members">{activemembers}</td>\n')
        outrow.append('  <td class="goals">{goalsmet}</td>\n')
        outrow.append('  <td class="loc">{place}<br />{address}<br />{city}, {state} {zip}</td>')
        outrow.append('  <td class="mtg">{meetingday}<br />{meetingtime}</td>')
        outrow.append('</tr>')
        outfile.write(('\n'.join(outrow)).format(**row))
        
    closearea(outfile)
    closediv(outfile)
    outfile.write("</body></html>\n")
    outfile.close()
