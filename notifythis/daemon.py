#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Modified from http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
### BEGIN LICENSE
# Copyright (C) 2009 Didier Roche <didrocks@ubuntu.com>
#This program is free software: you can redistribute it and/or modify it 
#under the terms of the GNU General Public License version 3, as published 
#by the Free Software Foundation.
#
#This program is distributed in the hope that it will be useful, but 
#WITHOUT ANY WARRANTY; without even the implied warranties of 
#MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
#PURPOSE.  See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along 
#with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE


import sys, os, time, atexit
from signal import SIGTERM 
import gettext
from gettext import gettext as _

class Daemon(object):
    """
    A generic daemon new-style class.
    
    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile=None, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
    
    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced 
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError, e: 
            sys.stderr.write(_('fork #1 failed: %d (%s)\n') % (e.errno, e.strerror))
            sys.exit(1)
    
        # decouple from parent environment
        os.chdir("/") 
        os.setsid() 
        os.umask(0) 
    
        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit from second parent
                sys.exit(0) 
        except OSError, e: 
            sys.stderr.write(_('fork #2 failed: %d (%s)\n') % (e.errno, e.strerror))
            sys.exit(1) 
    
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
    
        # write pidfile, if present
        if self.pidfile:
            atexit.register(self.delpid)
            pid = str(os.getpid())
            file(self.pidfile,'w+').write("%s\n" % pid)
    
    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        pid = None
        try:
            if self.pidfile:
                pf = file(self.pidfile,'r')
                pid = int(pf.read().strip())
                pf.close()
        except IOError:
            pid = None
    
        if pid:
            message = _('pidfile %s already exist. Daemon already running?\n')
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        
        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        if self.pidfile:
            try:
                pf = file(self.pidfile,'r')
                pid = int(pf.read().strip())
                pf.close()
            except IOError:
                pid = None
        
            if not pid:
                message = _('pidfile %s does not exist. Daemon not running?\n')
                sys.stderr.write(message % self.pidfile)
                return # not an error in a restart

            # Try killing the daemon process    
            try:
                while 1:
                    os.kill(pid, SIGTERM)
                    time.sleep(0.1)
            except OSError, err:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """
