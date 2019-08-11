#!/usr/bin/env python3
""" Make the featured club inclusion from the Google spreadsheet """

import tmutil, sys
import tmglobals
myglobals = tmglobals.tmglobals()
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
    myglobals.setup(parms)
    allclubs = Club.getClubsOn(myglobals.curs)
    
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
        i = 0
        for club in clubs:
            i += 1
            outfile.write('<div class="clubinfo" onclick="jQuery(\'#club%dopen, #club%dclosed, #club%dinfo\').toggle()">\n' % (i, i, i))
            outfile.write('<span id="club%dopen" style="display: none;">&#x2296;</span>\n' % i)
            outfile.write('<span id="club%dclosed" style="display: inline;">&#x2295;</span>\n' % i)
            outfile.write('<b>%s</b> - %s - %s - %s\n' % (club.clubname, club.meetingday, club.meetingtime, club.city))
            outfile.write('</div>')
            
            outfile.write('<div id="club%dinfo" style="display: none; margin-left: 1em; margin-bottom: 1em;">\n' % i)
            outfile.write('<p>')
            locparts = '<br />'.join([p for p in (club.location, club.streetaddress, '%s, %s %s' % (club.city, club.state, club.zip)) if p])
            outfile.write(locparts)
            outfile.write('</p>\n')
            conparts = []
            if club.contact:
                conparts.append(club.contact)
            if club.contactemail:
                conparts.append('<a href="mailto:%s">%s</a>' % (club.contactemail, club.contactemail))
            if club.contactphone:
                conparts.append(club.contactphone)
            club.contact = ', '.join(conparts)
            if club.contact:
                outfile.write('<p>Contact: %s</p>\n' % club.contact)
            if club.notes:
                outfile.write('<p>%s</p>\n' % club.notes)
            outfile.write('</div>\n')
            
    