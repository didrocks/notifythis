#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import dbus
import logging
import dbus.service
import dbus.mainloop.glib
import gobject
import os
import sys
import gettext
from gettext import gettext as _


from notifythis import checknotif
from notifythis.daemon import Daemon

class DbusHandler(dbus.service.Object):
    '''dbus service listener'''
    
    def __init__(self, session_bus, dbus_object, daemon):
        dbus.service.Object.__init__(self, session_bus, dbus_object)
        self.daemon = daemon
    
    @dbus.service.method("net.launchpad.DaemonInterface",
                     in_signature='', out_signature='')
    def ReloadConfig(self):
        logging.info(_("Receive reloading signal"))
        self.daemon.updateconfig()
    
    @dbus.service.method("net.launchpad.DaemonInterface",
                     in_signature='', out_signature='')
    def Exit(self):
        logging.info(_("Closing signal received"))
        self.daemon.mainloop.quit()


class DestkopDaemon(Daemon):
    '''Redefinied daemon using dbus'''
    
    def __init__(self, config_file, log_daemon_file):
        
        log_daemon_file = os.path.expanduser(log_daemon_file)
        try:
            if not os.path.exists(os.path.dirname(log_daemon_file)):
                os.makedirs(os.path.dirname(log_daemon_file))
            # make a first write to ensure we have the permission
            open(log_daemon_file, 'a').write(_("Realizing new daemon operation.\n"))
        except OSError, error:
            logging.error(_("Can't write in %s: %s") % (os.path.dirname(log_daemon_file), error))
            sys.exit(1)
        
        self.config_file = config_file
        self.dbus_object = None
        Daemon.__init__(self, stderr=os.path.expanduser(log_daemon_file))

        # initiate dbus connection and connector only now (as it's a daemon now)
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.session_bus = dbus.SessionBus()


    def start(self):
        '''test if the daemon already exist and try to launch it'''

        try:
            daemonHandler = self.session_bus.get_object('net.launchpad.notifythis',
                                             '/DaemonHandler')
        except dbus.exceptions.DBusException:
            pass
        else:
            logging.error(_("One daemon instance of notifythis is already launched. Exiting."))
            sys.exit(1)
        Daemon.start(self)


    def stop(self):
        '''send dbus signal to end the daemon'''
        
        try:
            daemonHandler = self.session_bus.get_object('net.launchpad.notifythis',
                                             '/DaemonHandler')
        except dbus.exceptions.DBusException:
            logging.error(_("No notifythis daemon detected. Did you launch it interactively?"))
            sys.exit(1)
        else:
            daemonHandler.Exit(dbus_interface='net.launchpad.DaemonInterface')
            logging.info(_("Notifythis daemon ended"))
        
    def reload(self):
        '''reload configuration and xml file in the daemon'''
        
        try:
            daemonHandler = self.session_bus.get_object('net.launchpad.notifythis',
                                             '/DaemonHandler')
        except dbus.exceptions.DBusException:
            logging.error(_("No notifythis daemon detected. Did you launch it interactively?")) 
            sys.exit(1)
        else:
            daemonHandler.ReloadConfig(dbus_interface='net.launchpad.DaemonInterface')
            logging.info(_("Notifythis daemon reloaded"))

    def updateconfig(self):
        '''update from config loading new /etc file'''
        self.notifier = checknotif.Notifier(self.config_file)
    
    def notifiercall(self, function):
        '''metamethod use to call dynamically self.notifier
        
        Otherwise, timeout_add_seconds will be bound to old notifier'''
        return getattr(self.notifier, function)()
    
    def run(self):
        '''initiate dbus, create notifier object et call main loop'''
 
        # storing object is compulsory for mainloop getting aware about dbus related objects
        dbus_name = dbus.service.BusName("net.launchpad.notifythis", self.session_bus)
        self.mainloop = gobject.MainLoop()
        mainloop = self.mainloop
        self.dbus_object = DbusHandler(self.session_bus, '/DaemonHandler', self)
        dbus_object = self.dbus_object
        # load configuration file, check every second and add a ping every 2 minutes
        self.updateconfig()
        gobject.timeout_add_seconds(checknotif.CHECK_INTERVAL, self.notifiercall, 'check')
        gobject.timeout_add_seconds(checknotif.PING_INTERVAL, self.notifiercall, 'ping')

        self.mainloop.run()
