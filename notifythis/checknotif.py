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

from notifythis import handlexml

import datetime
import logging
import os
import pynotify
import sys
import gettext
from gettext import gettext as _

DEFAULT_DELTA_BETWEEN_XML_RELOAD = 30


class Notifier():

    def __init__(self, config_file):
        '''init notification system'''
        
        self.events = []
        self.delta_between_xml_reload = DEFAULT_DELTA_BETWEEN_XML_RELOAD
        try:
            self.update_from_config_file(config_file)
        except IOError, error:
            logging.error(_("Can't load configuration file: %s") % error)
            sys.exit(1)
            
        self.time_for_next_xml_load = datetime.datetime.now() + self.delta_between_xml_reload
        logging.debug(_('Init notification system'))
        if not pynotify.init("NotifyThis"):
            logging.debug(_('Init notification system'))
            sys.exit(1)
        # try to load events from XML files, in right order
        for xml_file in self.xml_files:
            logging.info("Load %s XML input file"  % xml_file)
            try:
                self.events = handlexml.loadXML(xml_file)
            except IOError, error:
                logging.warning(_('XMl file seems being no more accessible: %s') % error)
            else:
                if not self.events:
                    logging.warning(_("Can't perform initial loading of empty %s file: no event found") % xml_file)
                else:
                    break
        if not self.events:
            logging.error(_('No good XML file found'))
            sys.exit(1)

    def update_from_config_file(self, config_path_file):
        '''enable opening xml file'''
        
        # take specified config file, otherwise the one related to library
        # and finally, default to /etc/notifythis
        if not config_path_file:
            config_path_file = '/etc/notifythis'
        config_path_file = os.path.abspath(config_path_file)
        logging.info(_('Loading configuration from %s') % config_path_file)
        
        with open(config_path_file, 'r') as config_file:
            for line in config_file:
                fields = line.split('#')[0] # Suppress commentary after the value in configuration file and in full line
                fields = fields.split('=') # Separate variable from value
                # normally, we have two fields in "fields"
                if len(fields) == 2:
                    entry = fields[0].strip()
                    if entry == 'DELTA_BETWEEN_XML_RELOAD':
                        self.delta_between_xml_reload = datetime.timedelta(minutes=int(fields[1].strip()))
                    elif entry == 'XML_FILES':
                        self.xml_files = []
                        xml_files = [xml_file.strip() for xml_file in fields[1].split(';')]
                        # if relative path, it's relative to config_file
                        for xml_file in xml_files:
                            if not xml_file.startswith('/'):
                                xml_file = os.path.abspath(os.path.dirname(config_path_file) + '/' + xml_file)
                            self.xml_files.append(xml_file)


    def check_notif(self):
        '''check if there is an event to notify'''

        now = datetime.datetime.now()
        last_check_time = now - datetime.timedelta(seconds=1)
        for event in self.events:
            # min limit to not show all old notification at startup
            if (last_check_time < event.time <= now) and not event.notified:
                logging.info(_('Event %s found, initially scheduled at: %s') % (event.title, event.time.strftime('%Y-%m-%d %H:%M:%S')))
                image_path = ""
                if event.icon: image_path = "file://" + event.icon
                notif = pynotify.Notification(event.title, event.content, image_path)
                if event.priority.lower() == 'normal':
                    urgency = pynotify.NORMAL
                elif event.priority.lower() == 'critical':
                    urgency = pynotify.CRITICAL
                else:
                    urgency = pynotify.URGENCY_LOW
                notif.set_urgency(urgency)
                if not notif.show():
                    logging.error(_('Failed to send notification'))
                # for limite case, mark item as shown (not display two times)
                event.notified = True

    def ping(self):
        '''Show ping in log'''
        logging.info(_('CheckNotify daemon ping')) 
        return True
        
    def updatexml(self):
        '''load from XML file'''
    
        # try to reload events from XML files, in right order
        now = datetime.datetime.now()
        if self.time_for_next_xml_load < now:
            for xml_file in self.xml_files:
                logging.info(_('Reloading %s XML input file') % xml_file)
                try:
                    new_events = handlexml.loadXML(xml_file)
                except IOError, error:
                    logging.warning(_('XMl file seems being no more accessible: %s') % error)
                else:
                    if not new_events:
                        logging.warning(_("Can't perform initial loading of empty %s file: no event found") % xml_file)
                    else:
                        self.events = new_events
                        self.time_for_next_xml_load = now + self.delta_between_xml_reload
                        break
            if not self.events:
                logging.error(_('No good XML file found. Keep old one.'))

    def check(self):
        '''update xml file and events at each interval'''
        
        self.updatexml()
        self.check_notif()
        return True # so that timeout-add continue to launch this function
