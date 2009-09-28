#!/usr/bin/env python
# -*- coding: utf-8 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

from . import handlexml

import datetime
import logging
import os
import pynotify
import sys

DEFAULT_DELTA_BETWEEN_CHECK = 60
DEFAULT_DELTA_BETWEEN_XML_RELOAD = 30


class Notifier():

    def __init__(self, config_file):
        '''init notification system'''
        
        self.events = []
        try:
            self.update_from_config_file(config_file)
        except IOError, error:
            logging.error("Can't load configuration file: %s" % error)
            sys.exit(1)
            
        self.time_for_next_xml_load = datetime.datetime.now() + self.delta_between_xml_reload
        logging.debug("Init notification system")
        if not pynotify.init("NotifyThis"):
            logging.debug("Init notification system")
            sys.exit(1)
        # try to load events from XML files, in right order
        for xml_file in self.xml_files:
            logging.info("Load %s XML input file"  % xml_file)
            try:
                self.events = handlexml.loadXML(xml_file)
            except IOError, error:
                logging.warning("XMl file seems being no more accessible: %s" % error)
            else:
                if not self.events:
                    logging.warning("Can't perform initial loading of empty %s file: no event found" % xml_file)
                else:
                    break
        if not self.events:
            logging.error("No good XML file found")
            sys.exit(1)


    def update_from_config_file(self, config_path_file):
        '''enable opening xml file'''

        self.delta_between_check = DEFAULT_DELTA_BETWEEN_CHECK
        self.delta_between_xml_reload = DEFAULT_DELTA_BETWEEN_XML_RELOAD
        
        # take specified config file, otherwise the one related to library
        # and finally, default to /etc/notifythis
        if not config_path_file:
            config_path_file = '/etc/notifythis'
        config_path_file = os.path.abspath(config_path_file)
        logging.info("Loading configuration from %s" % config_path_file)
        
        with open(config_path_file, 'r') as config_file:
            for line in config_file:
                fields = line.split('#')[0] # Suppress commentary after the value in configuration file and in full line
                fields = fields.split('=') # Separate variable from value
                # normally, we have two fields in "fields"
                if len(fields) == 2:
                    entry = fields[0].strip()
                    if entry == 'DELTA_BETWEEN_CHECK':
                        self.delta_between_check = int(fields[1].strip())
                    elif entry == 'DELTA_BETWEEN_XML_RELOAD':
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
        last_check_time = now - datetime.timedelta(seconds=self.delta_between_check)
        logging.info("New check, time: %s" % now.strftime('%Y-%m-%d %H:%M:%S'))   
        for event in self.events:
            # min limit to not show all old notification at startup
            if (last_check_time < event.time <= now) and not event.notified:
                logging.info("Event %s found, initially scheduled at: %s" % (event.title, event.time.strftime('%Y-%m-%d %H:%M:%S')))
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
                    logging.error("Failed to send notification")
                # for limite case, mark item as shown (not display two times)
                event.notified = True
                
    def updatexml(self):
        '''load from XML file'''
    
        # try to reload events from XML files, in right order
        now = datetime.datetime.now()
        if self.time_for_next_xml_load < now:
            for xml_file in self.xml_files:
                logging.info("Reloading %s XML input file" % xml_file)
                try:
                    new_events = handlexml.loadXML(xml_file)
                except IOError, error:
                    logging.warning("XMl file seems being no more accessible: %s" % error)
                else:
                    if not new_events:
                        logging.warning("Can't perform initial loading of empty %s file: no event found" % xml_file)
                    else:
                        self.events = new_events
                        self.time_for_next_xml_load = now + self.delta_between_xml_reload
                        break
            if not self.events:
                logging.error("No good XML file found. Keep old one")

