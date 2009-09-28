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

        
