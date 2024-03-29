#!/usr/bin/env python3
""" Make the CAP page inclusions from the Google spreadsheet """

import tmutil, sys
import tmglobals
myglobals = tmglobals.tmglobals()
import re
import gspread
from simpleclub import Club
from collections import OrderedDict

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

def makeint(v):
    try:
        v = int(v)
    except ValueError:
        v = 0
    return(v)

    
class Ambassador:
    def __init__(self, row):
        for key in row:
            nkey = tmutil.normalize(key)
            # Make sure columns that should be numbers are!
            if 'name' not in nkey:
                row[key] = makeint(row[key])
            setattr(self, nkey, row[key])
        self.name = self.firstname.strip() + ' ' + self.lastname.strip()
    
    def sortkey(self):
        if self.points > 0:
            return (0-self.points, 0, self.name)
        else:
            return (0, 0-self.nond101visits, self.name.lower())
    
class VisitedClub:
    
    def __init__(self, row):
        for key in row:
            nkey = tmutil.normalize(key)
            if nkey == 'visits':
                row[key] = makeint(row[key])
            setattr(self, nkey, row[key])

        if self.clubnumber:
            self.clubnumber = '%d' % self.clubnumber
            try:
                self.clubname = allclubs[self.clubnumber].clubname
            except KeyError:
                pass
            
        if self.clubname.endswith('*'):
            self.clubname = self.clubname[:-1]
                
    def sortkey(self):
        return (0-self.visits, self.clubname)
        

    

if __name__ == "__main__":
 
    import tmparms
    
    # Establish parameters
    parms = tmparms.tmparms()
    parms.add_argument('--capsheet', default='')
    parms.add_argument('--outprefix', default='${workdir}/cap')
    parms.add_argument('--minvisits', default=1, type=int)
    parms.add_argument('--listexternal', action='store_true')
    # Add other parameters here
    # Do global setup
    myglobals.setup(parms)
    allclubs = Club.getClubsOn(myglobals.curs)
    
    # Open the spreadsheet
    gc = gspread.authorize(tmutil.getGoogleCredentials())
    book = gc.open_by_url(parms.capsheet)
    
    # Get totals
    sheet = book.worksheet('Totals')
    d101total = int(sheet.cell(1, 2).value)
    nond101total = int(sheet.cell(2, 2).value)
    totalvisits = int(sheet.cell(3, 2).value)
    featuredtotal = int(sheet.cell(4, 2).value)
    
    # Start with the Ambassadors sheet
    sheet = book.worksheet('Ambassadors')
    
    # Get the 'as of' date
    asof = sheet.cell(1, 2).value
    with open(parms.outprefix+'asof.shtml', 'w') as outfile:
        outfile.write('<p>Information current as of %s.</p>\n' % asof)
    
    
    # Work through the ambassadors list

            
        
    ambassadors = []        
    for row in sheet.get_all_records(head=2, empty2zero=True):
        if (row['First Name'] + row['Last Name']) == 0 or (row['First Name']==' '  or row['Last Name']==' '):
            break
        #print(row['First Name'],type(row['First Name']),row['Last Name'],type(row['Last Name']))
        #if type(row['First Name']) !=int or  type(row['Last Name'] !=int ):
        ambassadors.append(Ambassador(row)) 
        
    # Sort by points, then name:
    ambassadors.sort(key=lambda r:r.sortkey())
    
    # Generate the output
    with open(parms.outprefix+'ambassadors.shtml', 'w') as outfile:
        info = []
        if totalvisits > 0:
            info.append('Our Club Ambassadors have made %s' % nicely(totalvisits, 'visit'))
        if featuredtotal > 0:
            info.append('including %s to featured clubs' % nicely(featuredtotal, 'visit'))
        if nond101total > 0:
            if featuredtotal > 0:
                info.append('and')
            else:
                info.append('including')
            info.append('%s to non-District 101 clubs: ' % nicely(nond101total, 'visit'))
            
        outfile.write('%s\n' % ' '.join(info))
    
        names = []
        for a in ambassadors:
            info = []
            if a.points > 0:
                info.append(nicely(a.points, 'point'))
            if a.nond101visits > 0:
                info.append(nicely(a.nond101visits, 'non-D101 visit'))
                
            names.append('<span class="altname"><b>%s</b></span>&nbsp;(%s)' % (a.name.replace(' ','&nbsp;'), ',&nbsp;'.join(info)))

        outfile.write(makenamelist(names))
        outfile.write('.\n')
                 
    # Now, the clubs
    sheet = book.worksheet('Clubs')
    visited = []
    for row in sheet.get_all_records():
        visited.append(VisitedClub(row))
      
    # Sort  
    visited.sort(key=lambda c:c.sortkey())
                

    with open(parms.outprefix+'clubs.shtml', 'w') as outfile:
        clublist = []
        nond101list = []
        vcount = 0
        for club in visited:
            if club.nond101location.strip():
                nond101list.append('<span class="altname">%s</span>&nbsp;(%s)' % (club.clubname.replace(' ','&nbsp;'), club.nond101location.replace(' ', '&nbsp;')))
            else:
                if club.visits != vcount:
                    if clublist:
                        outfile.write(makenamelist(clublist))
                        outfile.write('</p>\n')
                    outfile.write('<p><b>%s</b>:<br />\n' % nicely(club.visits, 'visit'))
                    clublist = []
                    vcount = club.visits
                clublist.append('<span class="altname">%s</span>' % club.clubname.replace(' ', '&nbsp;'))
                
        if clublist:
            outfile.write(makenamelist(clublist))
            outfile.write('</p>\n')
        
        # Now, if there are any external clubs, list tnem:
        if nond101list and parms.listexternal:
            outfile.write('<h3 class="beyond">Clubs Visited Beyond District 101:</h3>\n')
            outfile.write(makenamelist(nond101list))
            outfile.write('\n')        
        
    # Create the insight listing
    sheet = book.worksheet('Insights')
    sections = OrderedDict()  # Ensure keys are kept in order
    lastsectionname = None
    for row in sheet.get_all_records():
        sectionname = row['Section']
        if not sectionname:
            sectionname = lastsectionname
        if sectionname not in sections:
            sections[sectionname] = []
        lastsectionname = sectionname
        sections[sectionname].append(row['Insight'])


    with open(parms.outprefix+'insights.shtml', 'w') as outfile:
        for (i, sectionname) in enumerate(sections.keys()):
            outfile.write(f'''<h4 onclick="jQuery('#sec{i}insights, #sec{i}open, #sec{i}closed').toggle();"><span id="sec{i}open" style="display:none;">&#x25be;</span><span id="sec{i}closed">&#x25b8;</span>{sectionname}</h4>\n''')
            outfile.write(f'''<div id="sec{i}insights" style="display:none;">\n''')
            outfile.write('<ul>\n')
            for insight in sections[sectionname]:
                if insight:
                    outfile.write(f'<li>{insight}</li>\n')
            outfile.write('</ul>\n')
            outfile.write('</div>\n')
            outfile.flush()
        
