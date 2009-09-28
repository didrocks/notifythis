#!/usr/bin/env python
# -*- coding: utf-8 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

from . import eventtype

class Event:
    '''Event contain title, description, time and type
    
    type properties can be overrident by event properties.'''
    
    def __init__(self, title, content, time, type, priority=None, icon=None):
        self.reloadparameters(title, content, time, type, priority, icon)

    def reloadparameters(self, title, content, time, type, priority=None, icon=None):
        '''Enable reloading all parameters, taking overriding into account'''
    
        self.title = title
        self.content = content
        self.time = time
        self.type = type
        self.notified = False
        if not icon:
            self.icon = type.icon
        else:
            self.icon = icon
        if not priority: self.priority = type.priority 

        
