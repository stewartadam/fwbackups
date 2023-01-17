# -*- coding: utf-8 -*-
#  Copyright (C) 2006, 2007, 2008, 2009, 2010 Stewart Adam
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
import sys
import getpass
import pathlib
from enum import Enum, auto

MSWINDOWS = sys.platform.startswith('win')
LINUX = sys.platform.startswith('linux')
DARWIN = sys.platform == 'darwin'
IS_FLATPAK = os.path.exists('/.flatpak-info')

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
INSTALL_DIR = os.path.abspath(os.path.dirname(__file__))
USERHOME = pathlib.Path.home()

LOC = USERHOME.joinpath('.fwbackups')  # The fwbackups configuration directory
SETLOC = LOC.joinpath('Sets')  # The location to store set configuration files
ONETIMELOC = LOC.joinpath('fwbackups-OneTime.conf')  # The location to store the one-time backup configuration file
PREFSLOC = LOC.joinpath('fwbackups-prefs.conf')  # The location of the preferences file
RESTORELOC = LOC.joinpath('fwbackups-Restore.conf')  # The location to store the restore configuration file
LOGLOC = LOC.joinpath('fwbackups-userlog.txt')  # The location to store the log file

try:  # because Windows doesn't do exit codes properly...
    EXIT_STATUS_OK = os.EX_OK
except AttributeError:  # ... we need this thing.
    EXIT_STATUS_OK = 0

CRON_SIGNATURE = "# autogenerated by fwbackups"


class EventType(Enum):
    BACKUP_STARTED = auto()
    BACKUP_COMPLETE = auto()
    BACKUP_ERROR = auto()
    BACKUP_CANCELLED = auto()
    RESTORE_STARTED = auto()
    RESTORE_COMPLETE = auto()
    RESTORE_ERROR = auto()
    RESTORE_CANCELLED = auto()


def ConvertPath(path):
    """Makes a path portable."""
    if MSWINDOWS and path[1:3] != ':\\':
        path = '%s\\%s' % (ROOTDRIVE, path)
    return os.path.normpath(path)
