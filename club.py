import codecs
class Club:
    
    @classmethod
    def setHeaders(self, headers):
        self.headers = headers
    
    @classmethod
    def fixcn(self, s):
        try:
            return('%d' % int(s))
        except:
            return None
            
    def __init__(self, row):
        for i in range(len(self.headers)):
            h = self.headers[i]
            try:
                self.__dict__[h] = row[i].strip()
            except IndexError:
                self.__dict__[h] = ''
        self.clubnumber = self.fixcn(self.clubnumber)
        self.dcplastyear = ' '
        self.isvalid = False   # So we can handle ancient clubs if need be
        self.citygeo = None
        self.area = self.area.lstrip('0')
        
    def info(self):
        # Return a key for sorts and compares
        ret = {'number': self.clubnumber,
               'name' : self.clubname,
               'addr1' : self.address1,
               'addr2' : self.address2,
               'city': self.city,
               'state': self.state,
               'zip': self.zip,
               'time': self.meetingtime,
               'date': self.meetingday,
               'open': self.clubstatus,  
               'advanced': self.advanced,
               'division': self.division,
               'area': self.area
           }

        return ret
 
            
    def __repr__(self):
        return self.clubnumber + ' ' + self.clubname + ' is in %s' % self.city
        
    def makevalid(self):
        self.isvalid = True
        
    def addinfo(self, row, headers, only=None):
        """Add information to a club.  If 'only' is specified, only those columns are kept."""
        for i in range(len(headers)):
            h = headers[i]
            if not only or h in only:
                try:
                    self.__dict__[h] = row[i].strip()
                except IndexError:
                    self.__dict__[h] = ''
        self.isvalid = True
            
    def setcolor(self):
        members = int(self.activemembers)
        if members <= 12:
            self.color = "Red"
        elif members < 20:
            self.color = "Yellow"
        else:
            self.color = "Green"
            
    def setgeo(self, citygeo):
        self.citygeo = citygeo
        
            
    def setcounty(self, county):
        self.county = county

        
    def cleanup(self):
        if self.clubstatus.strip() == 'Open to all':
            self.clubstatus = 'Open'
        else:
            self.clubstatus = 'Restricted'
        if not self.isvalid:
            print 'not valid: ', self
            
