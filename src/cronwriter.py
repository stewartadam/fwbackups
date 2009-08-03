#!/usr/bin/python
# -*- coding: utf-8 -*-
#    Copyright (C) 2007, 2008, 2009 Stewart Adam
#    This file is part of fwbackups.

#    fwbackups is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

#    fwbackups is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with fwbackups; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
A simple program to take args and write them to a file
The trick is when executing crontab -e, the first arg passes
is the name of the /tmp file -- Guess what this grabs and
writes to ;)
"""
import sys
myname = sys.argv[0]
try:
    crontab = sys.argv[1]
except:
    print 'No file to write to! Exiting'
    sys.exit(1)
if crontab.endswith(".py"):
    print 'I will not overwrite a python file.'
    sys.exit(1)
ct = open(crontab, 'w')
contents = ''
for i in sys.stdin.readlines():
    if not i.endswith('\n'):
        i += '\n'
    contents += i
ct.write(contents)
ct.close()
