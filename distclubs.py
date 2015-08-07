#!/usr/bin/python
""" Generate the "Distinguished Clubs" report based on the current club statistics. """

import sys,  os.path
import tmutil, dbconn



class Myclub():
    def __init__(self, division, area, clubname, dstat):
        self.division = division
        self.area = area
        self.clubname = clubname
        self.clubdistinguishedstatus = dstat
        
def writeheader(outfile):    

	outfile.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html>
    <head>
    <meta http-equiv="Content-Style-Type" content="text/css">
    <title>Distinguished Club Report</title>
    <style type="text/css">
    

	html {font-family: Arial, "Helvetica Neue", Helvetica, Tahoma, sans-serif;
	      font-size: 75%;}

	table {font-size: 12px; border-width: 1px; border-spacing: 0; border-collapse: collapse; border-style: solid;}
	td, th {border-color: black; border-width: 1px; border-style: solid; text-align: center; vertical-align: middle;
	    padding: 2px;}

	.name {text-align: left; font-weight: bold; width: 22%;}
        .division {text-align: left; font-weight: bold; width: 5%;}
        .area {text-align: left; font-weight: bold; width: 5%;}
	.edate {border-left: none; font-weight: bold; width: 8%}
	.belowmin {border-left: none; font-weight: bold; width: 8%;}
	.number {text-align: right; width: 5%;}
	.goals {border-left: none;}
	.wide {width: 30% !important;}

	.green {background-color: lightgreen; font-weight: bold;}
	.yellow {background-color: yellow;}
	.red {background-color: red;}
	.rightalign {text-align: right;}
	.sep {background-color: #E0E0E0; padding-left: 3px; padding-right: 3px;}
	.greyback {background-color: #E0E0E0; padding-left: 3px; padding-right: 3px;}

	.madeit {background-color: lightblue; font-weight: bold;}
	.statushead {border-right: none; }
	.status {border-right: none; padding: 1px;}
	.reverse {background-color: black; color: white;}
	.bold {font-weight: bold;}
	.italic {font-style: italic;}
	.areacell {border: none;}
	.areatable {margin-bottom: 18pt; width: 100%; page-break-inside: avoid; display: block;}
	.suspended {text-decoration: line-through; color: red;}

	.divtable {border: none; break-before: always !important; display: block; float: none; position: relative; page-break-inside: avoid; page-break-after: always !important;}

	.divtable tfoot th {border: none;}
	.footinfo {text-align: left;}
	.dob {background-color: #c0c0c0;}
	.grid {width: 2%;}

	.todol {margin-top: 0;}
	.todop {margin-bottom: 0; font-weight: bold;}
	.status {font-weight: bold; font-size: 110%;}

	.clubcounts {margin-top: 12pt;}
	.finale {border: none; break-after: always !important; display: block; float: none; position; relative; page-break-after: always !important; page-break-inside: avoid;}

	@media print { 
	    body {-webkit-print-color-adjust: exact !important;}
			td {padding: 1px !important;}}
	</style>
    </head>
    <body>
""")

if __name__ == "__main__":
    import tmparms
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--date', dest='date', default='today')
    parms.add_argument('--outfile', dest='outfile', default='distclubs.html')
    parms.parse()
    if parms.quiet >= 1:
        def inform(*args):
            return
            
    # Connect to the database
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    thedate = tmutil.cleandate(parms.date)
    curs.execute("""SELECT division, area, clubname, clubdistinguishedstatus FROM clubperf WHERE
                    clubdistinguishedstatus <> "" AND asof = %s""", (thedate,))
    r = curs.fetchall()     
    outfile = open(parms.outfile, 'w')           
    
    



    pclubs = []
    sclubs = []
    dclubs = []


    for row in r:
        club = Myclub(*row)

        if club.clubdistinguishedstatus == 'D':
            dclubs.append(club)
        elif club.clubdistinguishedstatus == 'S':
            sclubs.append(club)
        elif club.clubdistinguishedstatus == 'P':
            pclubs.append(club)
    


    # Sort the clubs by division and area:
    pclubs.sort(key=lambda c: c.division + c.area)
    sclubs.sort(key=lambda c: c.division + c.area)
    dclubs.sort(key=lambda c: c.division + c.area)

    winners = [pclubs, sclubs, dclubs]
    names = ['President\'s Distinguished Clubs', 'Select Distinguished Clubs',
             'Distinguished Clubs']

    for (qualifiers, level) in zip(winners, names):
        outfile.write('<h4 id="%sclubs">%s</h4>\n' % (level[0],level))

        # And create the fragment
        outfile.write("""<table style="margin-left: auto; margin-right: auto; padding: 4px;">
          <tbody>
            <tr valign="top">
              <td><strong>Area</strong></td>
              <td><strong>Club</strong></td>
              <td><strong>&nbsp;</strong></td>
              <td><strong>Area</strong></td>
              <td><strong>Club</strong></td>
          </tr>
        """)
    # But now we want to go down, not across...
        incol1 = (1 + len(qualifiers)) / 2# Number of items in the first column.  
        left = 0  # Start with the zero'th item
        for i in range(incol1):
    		club = qualifiers[i]
    		outfile.write('<tr>\n')
    		outfile.write('  <td>%s%s</td><td>%s</td>\n' % (club.division, club.area, club.clubname))
    		outfile.write('  <td>&nbsp;</td>\n')
    		try:
    			club = qualifiers[i+incol1]   # For the right column
    		except IndexError:
    			outfile.write('<td>&nbsp;</td><td>&nbsp;</td>\n')    # Close up the row neatly
    			outfile.write('</tr>\n')
    			break
    		outfile.write('  <td>%s%s</td><td>%s</td>\n' % (club.division, club.area, club.clubname))
    		outfile.write('</tr>\n')
		
        outfile.write("""  </tbody>
        </table>
        """)

    outfile.close()

