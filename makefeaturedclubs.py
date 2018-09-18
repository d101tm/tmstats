#!/usr/bin/env python3
""" Make the featured club inclusion from the Google spreadsheet """

import tmutil, sys
import tmglobals
globals = tmglobals.tmglobals()
import re
import gspread
from simpleclub import Club

def makesortkey(s):
    # Strip non-alphameric characters and return all lower-case
    return ' '.join(re.split('\W+', s.lower())).strip()

    
def nicely(num, label):
    return '%d&nbsp;%s%s' % (num, label, 's' if num != 1 else '')
    
def makenamelist(names):
    if len(names) > 1:
        names[-1] = 'and ' + names[-1]
    if len(names) > 2:
        return(',\n'.join(names))
    else:
        return('\n'.join(names))

class FeaturedClub:
    
    def __init__(self, row):
        for key in row:
            nkey = tmutil.normalize(key)
            if nkey == 'clubnumber':
                setattr(self, nkey, row[key])
            else:
                val = ('%s' % row[key]).strip()
                if nkey not in( ('notes', 'contact')):
                    val = '&nbsp;'.join(val.split())
                setattr(self, nkey, val)

        if self.clubnumber:
            self.clubnumber = '%d' % self.clubnumber
            try:
                self.clubname = allclubs[self.clubnumber].clubname
            except KeyError:
                pass

        

    

if __name__ == "__main__":
 
    import tmparms
    
    # Establish parameters
    parms = tmparms.tmparms()
    parms.add_argument('--featured', default='https://docs.google.com/spreadsheets/d/19-imepV9YNq5N_g9GcBP5Ynq9BjTZP7kC_rLPnFAK7w/')
    parms.add_argument('--outfile', default='featuredclubs.shtml')
    # Add other parameters here
    # Do global setup
    globals.setup(parms)
    allclubs = Club.getClubsOn(globals.curs)
    
    # Open the spreadsheet
    gc = gspread.authorize(tmutil.getGoogleCredentials())
    book = gc.open_by_url(parms.featured)
    
    # Get totals
    sheet = book.sheet1
    
    clubs = []
        
    for row in sheet.get_all_records():
        if (not row['Club Name'].strip()):
            break
        clubs.append(FeaturedClub(row))
        
    # Sort by points, then name:
    clubs.sort(key=lambda c:c.clubname.lower())
    
    # Generate the output
    with open(parms.outfile, 'w') as outfile:
        outfile.write("""<style type="text/css">
table.featured {
  border: 1px solid #1C6EA4;
  width: 100%;
  text-align: left;
  vertical-align: top;
  border-collapse: collapse;
}
table.featured td, table.featured th {
  border: 1px solid #AAAAAA;
  padding: 3px 2px;
  vertical-align: top;
}

table.featured td. clubname {
  font-weight: bold;
}

table.featured tr:nth-child(even) {
  background: #f2df74;
}
table.featured thead {
  background: #772432;
  background: -moz-linear-gradient(top, #995b65 0%, #843a46 66%, #772432 100%);
  background: -webkit-linear-gradient(top, #995b65 0%, #843a46 66%, #772432 100%);
  background: linear-gradient(to bottom, #995b65 0%, #843a46 66%, #772432 100%);
}
table.featured thead th {
  font-size: 15px;
  font-weight: bold;
  color: #FFFFFF;
  border-left: 2px solid #D0E4F5;
}
table.featured thead th:first-child {
  border-left: none;
}

table.featured tfoot td {
  font-size: 14px;
}
table.featured tfoot .links {
  text-align: right;
}
table.featured tfoot .links a{
  display: inline-block;
  background: #1C6EA4;
  color: #FFFFFF;
  padding: 2px 8px;
  border-radius: 5px;
}
</style>
""")        
        outfile.write('<table class="featured">\n')
        outfile.write('<thead>\n')
        outfile.write('<tr><th>')
        outfile.write('</th><th>'.join(('Club', 'Meeting Time', 'Location', 'Contact', 'Notes')))
        outfile.write('</th></tr>\n')
        outfile.write('</thead>\n<tbody>\n')
        for club in clubs:
            outfile.write('<tr>')
            outfile.write('<td class="clubname">%s</td>\n' % club.clubname.replace(' ', '&nbsp;'))
            outfile.write('<td>%s<br />%s</td>\n' % (club.meetingtime, club.meetingday))
            locparts = '<br />'.join([p for p in (club.location, club.streetaddress, '%s, %s %s' % (club.city, club.state, club.zip)) if p])
            outfile.write('<td>%s</td>' % locparts)
            conparts = []
            if club.contact:
                conparts.append(club.contact)
            if club.contactemail:
                conparts.append('<a href="mailto:%s">%s</a>' % (club.contactemail, club.contactemail))
            if club.contactphone:
                conparts.append(club.contactphone)
            club.contact = ',<br />'.join(conparts)
            outfile.write('<td>%s</td>' % (club.contact if club.contact else '&nbsp;'))
            outfile.write('<td>%s</td>' % (club.notes if club.notes else '&nbsp;'))
            outfile.write('</tr>\n')
        outfile.write('</tbody>\n</table>\n')
        