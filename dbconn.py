""" Handle database connections for the TMSTATS suite """

import MySQLdb as mysql


    
class Singleton(object):
    def __new__(type, *args, **kwargs):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance
    
class dbconn(Singleton):
    def __init__(self, dbhost='localhost', dbuser=None, dbpass=None, dbname=None):
        if self.__dict__.get('conn', False):
            return
        self.dbhost = dbhost 
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbname = dbname
        #print("Connecting to %s %s with pw %s db %s" % (self.host, self.dbuser, self.dbpassword, self.dbname))
        self.conn = mysql.connect(self.dbhost, self.dbuser, self.dbpass, self.dbname, use_unicode=True, charset='UTF8')
        
    def cursor(self):
        return self.conn.cursor()
        
    def commit(self):
        return self.conn.commit()
        
    def close(self):
        self.conn.close()
        self.conn = None
        
if __name__ == '__main__':
    import tmparms, tmglobals

    parms = tmparms.tmparms()
    globals = tmglobals.tmglobals(parms)
    #print('Connecting to %s:%s as %s' % (parms.dbhost, parms.dbname, parms.dbuser))
    conn = globals.conn
    curs = globals.curs

    curs.execute('show tables')
    print('Tables:\n%s' % '\n'.join('  ' + p[0] for p in curs.fetchall()))
    conn.close()
