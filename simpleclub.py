""" Simple class to maintain information about a club.
"""
class Club:
    """ Keep information about a club """
    @classmethod
    def setfields(self, names):
        self.fieldnames = names
        self.badnames = ['firstdate', 'lastdate']
        self.goodnames = [n for n in names if n not in self.badnames]
        
    @classmethod
    def getClubsOn(self, date, curs, setfields=False):
        """ Get the clubs which were in existence on a specified date """
        curs.execute("SELECT * FROM clubs WHERE firstdate <= %s AND lastdate >= %s", (date, date))
        if setfields:
            # Get the fieldnames before we get anything else:
            fieldnames = [f[0] for f in curs.description]
            Club.setfields(fieldnames)
    
        res = {}
    
        # OK, now build the list of clubs at the beginning of the period
        for eachclub in curs.fetchall():
            club = Club(eachclub)
            res[club.clubnumber] = club
            
        return res
        
    
    def __init__(self, values):
        self.cmp = []
        for (name, value) in zip(self.fieldnames, values):
            self.__dict__[name] = value
            if name not in self.badnames:
                self.cmp.append(value)
     
    def __eq__(self, other):
        return self.cmp == other.cmp
         
    def __ne__(self, other):
        return self.cmp != other.cmp
        
    def delta(self, other):
        """ Return tuples of (name, self, other) for any values which have changed """
        res = []
        for name in self.goodnames:
            if self.__dict__[name] != other.__dict__[name]:
                res.append((name, self.__dict__[name], other.__dict__[name]))
        return res
        
    def __repr__(self):
        return '; '.join(['%s = "%s"' % (name, self.__dict__[name]) for name in self.goodnames])
