#!/usr/bin/env python
# -*- coding: utf-8 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

import datetime
import logging
import os
import urllib
import xml.etree.ElementTree as etree

from . import eventtype
from . import event

#var_directory = '/var/cache/notify-this'
var_directory = '/tmp'

class IconDict(dict):
    '''icon dictionnary to handle http cache'''

    def __init__(self):
        self.data = {}

    def __getitem__(self, key): return self.data[key]

    def __setitem__(self, key, value):
        '''cache webfile if reachable and set value to real file value'''
      
        if key in self.data: # if already cached
            logging.debug('Icon "%s" already cached' % key)
            return
        
        logging.debug('Caching "%s" icon' % key)
        # cache this file if accessed by http://
        if value.startswith("http://"):
            local_image = urllib.urlopen(key)
            dest_name = var_directory + os.path.basename(key)
            if not os.path.exists(var_directory):
                logging.warning('Trying to creating %s directory' % var_directory)
                os.makedir(var_directory)
            logging.debug('Downloading "%s" to "%s"' % (key, dest_name))
            with open(dest_name,'wb') as dest_file:
                dest_file.write(local_image.read())
            self.data[key] = dest_name
        else:
            if not os.path.exists(key):
                logging.warning('%s icon file does not exist, notification will be shown without any image' % key)
                self.data[key] = None
            else:
                self.data[key] = value


def loadXML(xml_url):
    '''load XML file, locally or on the web (http://)'''
    
    xml_namespace = '{http://launchpad.net/notify-this}'    
    types = {}
    events = []
    # deal with cache and avoid checking multiple times same file
    icons = IconDict()
    
    if xml_url.startswith('http://'):
        xml_file = urllib.urlopen(xml_url)
        # handle 404
        if xml_file.code == 404:
            raise IOError, "Error 404 on %s" % xml_url
    else:
        xml_file = open(xml_url, 'r')
    xml_tree = etree.parse(xml_file)
    xml_file.close()
    root = xml_tree.getroot()
    logging.debug("load event types")
    notiftype = root.find(xml_namespace + 'notiftypes')
    for xml_elem in notiftype.findall(xml_namespace + 'type'):
        name = xml_elem.find(xml_namespace + 'name').text
        priority = xml_elem.find(xml_namespace + 'priority').text
        # optional icon
        icon = None
        if xml_elem.find(xml_namespace + 'icon') is not None:
            icon = xml_elem.find(xml_namespace + 'icon').text
            icons[icon] = icon # cache icon and return new one if needed
            icon = icons[icon]
        logging.debug("Creating new event type: %s, %s, %s" % (name, priority, icon))
        types[name] = eventtype.EventType(name, priority, icon)
        
    logging.debug("load events")
    notifevents = root.find(xml_namespace + 'notifevents')
    for xml_elem in notifevents.findall(xml_namespace + 'event'):
        title = xml_elem.find(xml_namespace + 'title').text
        content = xml_elem.find(xml_namespace + 'content').text
        timeevent = datetime.datetime.strptime(xml_elem.find(xml_namespace + 'time').text, '%Y-%m-%d %H:%M')
        type_name = xml_elem.find(xml_namespace + 'type').text
        if not type_name in types:
            raise ValueError("Type '%s' in '%s' event does not exists" % (type_name, title))
        # optional values
        priority = None
        if xml_elem.find(xml_namespace + 'priority') is not None:
            priority = xml_elem.find(xml_namespace + 'priority').text
        icon = None
        if xml_elem.find(xml_namespace + 'icon') is not None:
            icon = xml_elem.find(xml_namespace + 'icon').text
            icons[icon] = icon # cache icon and return new one if needed
            icon = icons[icon]
        logging.debug("Creating new event: %s, %s, %s, %s, %s, %s" % (title, content, timeevent, types[type_name], priority, icon))
        events.append(event.Event(title, content, timeevent, types[type_name], priority, icon))

    return events
            
