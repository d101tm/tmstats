#!/usr/bin/env python3
""" Fixes up a development clone of the WordPress database """

import configparser
import os.path

import dbconn
import tmglobals
import tmutil

myglobals = tmglobals.tmglobals()



### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    
    # Establish parameters
    parms = tmparms.tmparms()
    # Add other parameters here
    parms.add_argument('--wpconfigfile', type=str, default='')

    # Do global setup
    myglobals.setup(parms,connect=False)

    # Parse the current user's .my.cnf file; this must have the username and password in the [client] section.
    msconfig = configparser.ConfigParser()
    msconfig.read(os.path.expanduser("~/.my.cnf"))
    username = msconfig.get("client", "user")
    password = msconfig.get("client", "password")

    if not parms.wpconfigfile:
        parms.wpconfigfile = os.path.join(parms.wpdir, 'wp-config.php')
    # Parse the WordPress configuration file
    config = tmutil.parseWPConfig(open(parms.wpconfigfile,'r'))

    # Connect as the active user, who needs full authority over WordPress
    print(f'connecting to {parms.dbhost} as {username} pw {password}')
    conn = dbconn.dbconn(parms.dbhost, username, password, '')
    curs = conn.cursor()

    # Make sure the WP user can access the database
    curs.execute("CREATE USER IF NOT EXISTS '%s'@'localhost' IDENTIFIED BY '%s'" % (config['DB_USER'], config['DB_PASSWORD']))
    ("GRANT ALL PRIVILEGES ON '%s'.'*' TO '%s'@'localhost'" % (config['DB_NAME'], config['DB_USER']))
    curs.execute("FLUSH PRIVILEGES")

    conn.close()


    # Connect to the WP database     
    conn = dbconn.dbconn(config['DB_HOST'], config['DB_USER'], config['DB_PASSWORD'], config['DB_NAME'])
    curs = conn.cursor()
    prefix = config['table_prefix']
    userstable = prefix + 'users'
    metatable = prefix + 'usermeta'

    # Ensure there's a privileged user named 'd101dev' with password 'd101dev'

    # Get the hash of the password
    curs.execute("SELECT MD5('d101dev')")
    hash = curs.fetchone()[0]
    
    stmt = "SELECT id FROM " + userstable + " WHERE user_login = 'd101dev'"
    curs.execute(stmt)
    res = curs.fetchone()
    if not res:
        # No d101dev user exists - must create one
        stmt = ("INSERT INTO " + userstable + " (user_login, user_pass, user_nicename, display_name, user_registered)" + " VALUES('d101dev', '%s', 'd101dev', 'd101dev', now())") % (hash, )
        curs.execute(stmt)
    else:
        # Update the d101dev user's password
        stmt = ("UPDATE " + userstable + " SET user_pass = '%s' WHERE ID = %s") %  (hash, res[0])
        curs.execute(stmt)

    # Get d101dev's id
    curs.execute("SELECT id FROM " + userstable + " WHERE user_login = 'd101dev'")
    id = curs.fetchone()[0]

    # Now we have to set the d101dev user as an Administrator - copy from user 1
    curs.execute("SELECT meta_key, meta_value FROM " + metatable + " WHERE user_id = 1")
    ans = curs.fetchall() 

    keys_to_copy = [prefix + 'capabilities', prefix + 'user_level', 'health_check', 'dismissed_wp_pointers']
    keys_to_copy = []
    for (key, value) in ans:
        if key in keys_to_copy:
            stmt = 'INSERT INTO ' + metatable + ' (user_id, meta_key, meta_value) VALUES (%s, %s, %s)'
            curs.execute(stmt, (id, key, value))


    conn.commit()
    conn.close()
