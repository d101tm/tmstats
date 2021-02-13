#!/usr/bin/env python3
""" Make Contest Page:

    Use the information from The Events Calendar to create a page with
    a complete listing of all contests in the District. 
"""

import dbconn, tmutil, sys, os
from datetime import datetime
import re
import tmglobals
import EventsCalendar
myglobals = tmglobals.tmglobals()

class Contest:
    def __init__(self, name, scope, event=None):
        self.name = name
        self.scope = scope
        self.event = event

    def __repr__(self):
        if not self.event:
            return f'<tr><td>{self.scope} {self.name}</td><td>TBA</td></tr>'
        else:
            name = f'<b>{self.event.title}</b>'
            date = self.event.start.strftime('%B %d').replace(' 0',' ')
            time = self.event.start.strftime(' %I:%M') + '-' + self.event.end.strftime(' %I:%M %p')
            time = time.replace(' 0', ' ').replace(' ','').lower()

        if parms.omitvenues:
            addr = ''
        else:
            addr = '<td>' + venuelist[self.event.venue].addr.replace('\n', '<br>') + '</td>'

        if parms.showpast or (self.event.start and self.event.start > parms.now):
            register = f' | <a href="{self.event.url}">Register</a>'
        else:
            register = ""
        ans = f'<tr><td>{name}<br /><a href="{self.event.name}">More Information</a>'\
              f'{register}</td><td><b>{date}</b><br>{time}{addr}</td></tr>'
        return ans






if __name__ == "__main__":

    import tmparms


    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--verbose', '-v', action='count')
    parms.add_argument('--uselocal', action='store_true')
    parms.add_argument('--outfile', type=str, default='${workdir}/contestschedule.html')
    parms.add_argument('--season', type=str, choices=['fall', 'spring', 'Fall', 'Spring', ''], default='')
    parms.add_argument('--year', type=int, default=0)
    parms.add_argument('--showpastregistration', dest='showpast', action='store_true')
    parms.add_argument('--registrationoptional', dest='registrationoptional', action='store_true')
    parms.add_argument('--omitvenues', action='store_true')

    # Do global setup
    myglobals.setup(parms)
    conn = myglobals.conn
    curs = myglobals.curs



    # Figure out the contest period.
    parms.now = datetime.now()
    parms.start = parms.now
    parms.end = parms.now
    if parms.now.month <= 6 or parms.season.lower() == 'spring':
        parms.start = parms.start.replace(month=1,day=1)
        parms.end = parms.end.replace(month=6,day=30)
    else:
        parms.start = parms.start.replace(month=7,day=1)
        parms.end = parms.end.replace(month=12,day=31)
    if parms.year:
        parms.start = parms.start.replace(year=parms.year)
        parms.end = parms.end.replace(year=parms.year)
    # Make the intervals inclusive of their whole days
    parms.start = parms.start.replace(hour=0, minute=0, second=0, microsecond=0)
    parms.end = parms.end.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Create contest placeholders for each Area and Division
    contests = {}
    curs.execute("SELECT district, division, area FROM areaperf WHERE entrytype='L' GROUP BY district, division, area")
    for (district, division, area) in curs.fetchall():
        if division != '0D':
            if division not in contests:
                contests[division] = Contest(division, 'Division')
            contests[division+area] = Contest(division+area, 'Area')

    conn.close()

    # Connect to the Events Calendar
    ec = EventsCalendar.EventsCalendar(parms)

    # Get relevant contest events
    eventlist = ec.getEvents('contest', startfrom=parms.start, endbefore=parms.end)

    # If there are no events, write out the 'tba' message and exit
    if not eventlist:
        with open(parms.outfile, 'w') as outfile:
            outfile.write('<p>No contests have yet been scheduled.</p>\n')
        sys.exit()

    # And get all venues for these contests
    venuelist = ec.getVenues()

    # If no venues are in the real world, we'll omit the location column
    realworld = False
    for v in venuelist.values():
        realworld = realworld or v.realworld


    # Now, put each contest into its place (or places, if it's multi-area)
    # If a contest covers multiple areas, remove any consecutive ones

    title_pattern = re.compile(r"""(Division|Area)\s+(.*)\s+Contest""")

    for e in eventlist.values():
        words = e.title.replace('/', ' ').split()
        scope = words.pop(0)
        units = []

        # Peel off the Areas or Divisions participating in this contest
        if scope == 'Division':
            while len(words[0]) == 1:
                units.append(words.pop(0))
        else:
            while len(words[0]) == 2:
                units.append(words.pop(0))

        # Reconstruct the name of the contest
        tail = '/'.join(units) + ' ' + ' '.join(words)
        e.title = scope + ' ' + tail

        # Delete the placeholders for this contest, if any.
        for u in units:
            try:
                del contests[u]
            except KeyError:
                pass

        # Now, insert the contest in the appropriate slots.
        last = None
        for u in units:
            if last and (u[0] == last[0]) and ((ord(u[-1]) - ord(last[-1])) == 1):
                # We don't need an entry for this unit after all; it's merged.
                pass
            else:
                contests[u + ' ' + tail] = Contest(u, scope, event=e)
            last = u

        if not e.url and not parms.registrationoptional:
            print(f'{e.title} does not have a Registration URL')


    # OK, we are finally ready to print!
    # If no event has a venue, we will ignore the venue column
    if not realworld:
        parms.omitvenues = True

    outfile = open(parms.outfile,'w')

    outfile.write("""<table border="1"><colgroup> <col> <col> <col> </colgroup>
    <thead>

    </thead>
    <tbody>\n""")
    outfile.write("<style>td.divhead {background: #F2DF74; font-size: 200%; font-weight: bold; text-align: center; border: none;}</style>\n")
    for c in sorted(contests.values(), key=lambda c:c.name):
        if c.scope == 'Division':
            if parms.omitvenues:
                outfile.write(f'<tr><td colspan="2" class="divhead">Division {c.name[0]}</td></tr>\n')
                outfile.write('<tr><td><b>Area/Division</b></td><td><b>When</b></td></tr>\n')
            else:
                outfile.write(f'<tr><td colspan="3" class="divhead">Division {c.name[0]}</td></tr>\n')
                outfile.write('<tr><td><b>Area/Division</b></td><td><b>When</b></td><td><b>Where</b></td></tr>\n')
        outfile.write(repr(c))

    outfile.write("""</tbody>
    </table>\n""")













