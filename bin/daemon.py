#!/usr/bin/env python

import sys, os

import syslog

def rundaemon(usermain, logfile = 'var/log/pydaemon.log',
              pidfile = '/var/run/pydaemon.pid',
              datadir='/root/data',
              userid=None, groupid=None):

    os.umask(0)
    
    # do the UNIX double-fork magic, see Stevens' "Advanced
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)            # exit first parent

    except OSError, e:
        syslog.syslog(syslog.ERR, "fork #1 failed: %d (%s)" % (e.errno, e.strerror))
        sys.exit(1)

    os.setsid()
    
    # decouple from parent environment
    os.chdir("/")   #don't prevent unmounting....

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent, print eventual PID before
            #print "Daemon PID %d" % pid
            open(pidfile,'w').write("%d"%pid)
            sys.exit(0)
    except OSError, e:
        syslog.syslog(syslog.ERR, "fork #2 failed: %d (%s)" % (e.errno, e.strerror))
        sys.exit(1)

    # start the daemon main loop
    # change to data directory if needed
    os.chdir(datadir)
    #redirect outputs to a logfile
    #    sys.stdout = sys.stderr = Log(open(logfile, 'a+'))
    #ensure the that the daemon runs a normal user
    if userid:
        os.setegid( userid )     #set group first "pydaemon"
    if groupid:
        os.seteuid( groupid )     #set user "pydaemon"
    #start the user program here:
    usermain()
