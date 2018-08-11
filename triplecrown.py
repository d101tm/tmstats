#!/usr/bin/env python3

""" Create the Triple Crown report """


import tmutil, sys, os
from datetime import date

import tmglobals
globals = tmglobals.tmglobals()



### Insert classes and functions here.  The main program begins in the "if" statement below.

winners = {}
class Winner:
    awards = ['CC', 'ACB', 'ACL', 'ACS', 'ACG', 'CL', 'ALB', 'ALS', 'DTM']
    
    @classmethod
    def add(self, name, award):
        if name not in winners:
            Winner(name) 
        item = winners[name]
        item.count[award] += 1
        
    def __init__(self, name):
        winners[name] = self
        self.count = {}
        for each in self.awards:
            self.count[each] = 0
            
    def __repr__(self):
        res = []
        for each in self.awards:
            if self.count[each] == 1:
                res.append(each)
            elif self.count[each] > 1:
                res.append("%s(%d)" % (each, self.count[each]))
        return ', '.join(res)

if __name__ == "__main__":
 
    import tmparms

    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--short', action='store_true')
    parms.add_argument('--tmyear', type=int, default=0)
    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    
    
    # Figure out the year
    tmyear = parms.tmyear
    if not tmyear:
        tmyear = globals.tmyear
    
    # Get the Triple Crown winners
    curs.execute("SELECT membername, award FROM awards WHERE membername IN (SELECT membername FROM (SELECT la.membername, lcount+ccount AS n FROM (SELECT membername, COUNT(DISTINCT award) AS lcount FROM awards WHERE award IN ('CL', 'ALB', 'ALS', 'DTM') AND tmyear = %s GROUP BY membername) la INNER JOIN (SELECT membername, COUNT(DISTINCT award) AS ccount FROM awards WHERE award IN ('CC', 'ACB', 'ACS', 'ACG') AND tmyear = %s GROUP BY membername) ca on la.membername = ca.membername AND la.lcount > 0 AND ca.ccount > 0 GROUP BY membername HAVING n >= 3 ORDER BY membername) winners) AND award != 'LDREXC' ORDER BY membername;", (tmyear, tmyear))
    for (name, award) in curs.fetchall():
        Winner.add(name, award)
    
    if parms.short:
        for name in sorted(winners.keys()):
            print('%s: %s' % (name, winners[name]))
    else:
        print("<table>")
        print("  <thead>")
        print("    <tr><th align='left'>Name</th><th align='left'>Awards</th></tr>")
        print("  </thead>")
        print("  <tbody>")
        for name in sorted(winners.keys()):
            print("    <tr><td style='padding-right: 20px;'>%s</td><td>%s</td></tr>" % (name, winners[name]))
        print("  </tbody>")
        print("</table>")
