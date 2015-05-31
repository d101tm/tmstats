#!/usr/bin/python
import os, sys
import MySQLdb as mysql
import yaml

parms = yaml.load(open('tmstats.yml','r'))
print parms
conn = mysql.connect(parms.get('host', 'localhost'), parms['dbuser'], parms['dbpassword'], parms['dbname'])
c = conn.cursor()
c.execute('create table foo')
print c.fetchall()
