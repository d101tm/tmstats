#!/usr/bin/python
""" Utility functions for the TMSTATS suite """

def cleandate(indate):
    from datetime import date, timedelta
    if '/' in indate:
        indate = indate.split('/')
        indate = [indate[2], indate[0], indate[1]]
    elif '-' in indate:
        indate = indate.split('-')
    elif 'today'.startswith(indate.lower()):
        return date.today().strftime('%Y-%m-%d')
    elif 'yesterday'.startswith(indate.lower()):
        return (date.today() - timedelta(1)).strftime('%Y-%m-%d')
    if len(indate[0]) == 2:
        indate[0] = "20" + indate[0]
    if len(indate[1]) == 1:
        indate[1] = "0" + indate[1]
    if len(indate[2]) == 1:
        indate[2] = "0" + indate[2]
    return '-'.join(indate)
    
