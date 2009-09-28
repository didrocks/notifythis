#!/usr/bin/env python
# -*- coding: utf-8 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

class EventType:
    '''EventType load name, priority and icon'''
    
    def __init__(self, name, priority, icon=None):
        
        self.name = name
        self.priority = priority
        self.icon = icon
        
