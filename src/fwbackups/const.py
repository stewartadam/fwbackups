# -*- coding: utf-8 -*-
#  Copyright (C) 2006, 2007, 2008, 2009 Stewart Adam
#  This file is part of fwbackups.

#  fwbackups is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.

#  fwbackups is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with fwbackups; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
All constants in the program
"""
import os
import os.path
import sys
import getpass

MSWINDOWS = sys.platform.startswith('win')
LINUX = sys.platform.startswith('linux')
DARWIN = sys.platform == 'darwin'
if MSWINDOWS:
  UID = 1
  ROOTDRIVE = os.path.splitdrive(sys.argv[0])[0]
else:
  UID = os.getuid()
  
try:
  USER = getpass.getuser()
except ImportError:
  USER = False

# Paths
INSTALL_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))

if MSWINDOWS:
  USERHOME = INSTALL_DIR
else:
  # Remember me: path, os.sep || newline, os.linesep
  USERHOME = os.path.expanduser('~%s' % USER) # The full path to the user's home
  if USERHOME == '~%s' % USER: # if the OS doesn't support that format
    USERHOME = os.path.expanduser('~')
LOC = os.path.join(USERHOME, '.fwbackups') # The fwbackups configuration directory
SETLOC = os.path.join(LOC, 'Sets') # The location to store set configuration files
ONETIMELOC = os.path.join(LOC, 'fwbackups-OneTime.conf') # The location to store the one-time backup configuration file
PREFSLOC = os.path.join(LOC, 'fwbackups-prefs.conf') # The location of the preferences file
RESTORELOC = os.path.join(LOC, 'fwbackups-Restore.conf') # The location to store the restore configuration file
LOGLOC = os.path.join(LOC, 'fwbackups-userlog.txt') # The location to store the log file

try: # because Windows doesn't do exit codes properly...
  EXIT_STATUS_OK = os.EX_OK
except: #... we need this thing.
  EXIT_STATUS_OK = 0
  
def ConvertPath(path):
  """Makes a path portable."""
  if MSWINDOWS and path[1:3] != ':\\':
    path = '%s\\%s' % (ROOTDRIVE, path)
  return os.path.normpath(path)
