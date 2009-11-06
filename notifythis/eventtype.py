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

import logging
import gettext
from gettext import gettext as _

class EventType:
    '''EventType load name, priority and icon'''
    
    def __init__(self, name, priority, icon=None):
        
        self.name = name
        self.priority = priority
        self.icon = icon
        logging.debug(_('Creating new event type: %s, %s, %s') % (name, priority, icon))
      
