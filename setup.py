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

###################### DO NOT TOUCH THIS (HEAD TO THE SECOND PART) ######################

try:
    import DistUtilsExtra.auto
except ImportError:
    import sys
    print >> sys.stderr, 'To build notifythis you need https://launchpad.net/python-distutils-extra'
    sys.exit(1)

assert DistUtilsExtra.auto.__version__ >= '2.10', 'needs DistUtilsExtra.auto >= 2.10'


DistUtilsExtra.auto.setup(
    name='notifythis',
    version='0.1',
    license='GPL-3',
    author='Didier Roche',
    author_email='didrocks@ubuntu.com',
    description='Easily notify information to user from data file …',
    long_description='NotifyThis is a daemon enabling notification from network or local xml files, showing icon, severity, caching data… The current use case is announcing conferences, lessons, as information during a party.',
    url='https://launchpad.net/notifythis',
    )

