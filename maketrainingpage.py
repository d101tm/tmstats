#!/usr/bin/env python3
""" Make Training Page:

    Use the information from The Events Calendar to create a page with
    a complete listing of all trainings in the District. 
"""

import sys
from datetime import datetime
import tmglobals
import EventsCalendar
myglobals = tmglobals.tmglobals()




class Training:
    def __init__(self, event):
        self.event = event

    def __repr__(self):

        name = f'<b>{self.event.title}</b>{self.event.specialnote}'
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
    parms.add_argument('--outfile', type=str, default='${workdir}/trainingschedule.html')
    parms.add_argument('--showpastregistration', dest='showpast', action='store_true')
    # Add other parameters here
    myglobals.setup(parms, connect=False)

 
      
    # Figure out the training period.
    parms.now = datetime.now()   
    parms.start = parms.now
    parms.end = parms.now  
    if parms.now.month >= 5 and parms.now.month <= 9:
        parms.start = parms.start.replace(month=6,day=1)
        parms.end = parms.end.replace(month=9,day=30)
    else:
        parms.start = parms.start.replace(month=11,day=1)
        parms.end = parms.end.replace(month=3,day=31)
        if parms.now.month >= 10:
            parms.end = parms.end.replace(year=parms.end.year+1)
        else:
            parms.start = parms.start.replace(year=parms.start.year-1)
    # But we don't care about past trainings, set start to today
    parms.start = parms.now.replace(hour=0,minute=0,second=0)
    parms.end = parms.end.replace(hour=23, minute=59, second=59, microsecond=999999)  # end of day

    # Connect to the Events Calendar
    ec = EventsCalendar.EventsCalendar(parms)

    # Get relevant training events
    eventlist = ec.getEvents('training', startfrom=parms.start, endbefore=parms.end)

    # If there are no events, write out the 'tba' message and exit
    if not eventlist:
        with open(parms.outfile, 'w') as outfile:
            outfile.write('<p>No training sessions are currently scheduled.</p>\n')
        sys.exit()

    # Get venues
    venuelist = ec.getVenues()

    # If no venues are in the real world, we'll omit the location column
    realworld = False
    for v in venuelist.values():
        realworld = realworld or v.realworld


    # Do we need to create a venue column?
    if realworld:
        # At least one event has a real venue, so we need it
        colgroup = '<col> <col> <col>'
        venuecol = '<th><b>Where</b></th>'
        parms.omitvenues = False
    else:
        colgroup = '<col> <col>'
        venuecol = ''
        parms.omitvenues = True
            

    outfile = open(parms.outfile,'w')
    outfile.write(f"""<table class="d101eventtable"><colgroup> {colgroup} </colgroup>
<thead>
<tr><th><b>Training</b></th><th><b>When</b></th>{venuecol}</tr>
</thead>
<tbody>\n""")
    for event in sorted(eventlist.values(),key=lambda l:l.start):
        outfile.write(repr(Training(event)))
    
    outfile.write("""</tbody>
    </table>\n""")
        
        
    

        
        
    
    
    
    
 
    
    
