""" Handle database connections for the TMSTATS suite """
import os, sys
import MySQLdb as mysql
import yaml

    
class Singleton(object):
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance
    
class dbconn(Singleton):
    def __init__(self, parmfile='tmstats.yml'):
        if self.__dict__.get('conn', False):
            return
        self.parms = yaml.load(open(parmfile,'r'))
        self.host = self.parms.get('host', 'localhost')
        self.dbuser = self.parms.get('dbuser','')
        self.dbpassword = self.parms.get('dbpassword','')
        self.dbname = self.parms.get('dbname','')
        #print "Connecting to %s %s with pw %s db %s" % (self.host, self.dbuser, self.dbpassword, self.dbname)
        self.conn = mysql.connect(self.host, self.dbuser, self.dbpassword, self.dbname)
        
    def cursor(self):
        return self.conn.cursor()
        
    def commit(self):
        return self.conn.commit()
        
    def close(self):
        self.conn.close()
        self.conn = None
        
if __name__ == '__main__':

    conn = dbconn()
    conn2 = dbconn()
    print conn
    print conn2
    print conn == conn2
    print conn.dbname == conn2.dbname
    print conn.conn == conn2.conn
    c = conn.cursor()
    c.execute('show tables')
    print c.fetchall()
    conn.commit()
    conn.close()
