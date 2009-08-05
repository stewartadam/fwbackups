#!/usr/bin/python
# -*- coding: utf-8 -*-
#  Copyright (C) 2005, 2006, 2007, 2008, 2009 Stewart Adam
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
import os
import sys
import time
import getopt
import signal

from fwbackups.i18n import _
from fwbackups.const import *
import fwbackups
from fwbackups.operations import backup
from fwbackups import config
from fwbackups import fwlogger

def usage(error=None):
  if error:
    print _('Error: %s'  % error)
    print _('Run with --help for usage information.')
  else:
    print _("""Usage: fwbackups-run [OPTIONS] Set_Name(s)
Options:
  -v, --verbose  :  Increase verbosity (print debug messages)
  -h, --help  :  Print this message and exit
  -l, --silent  :  Print messages to log file only

Set_Name(s) is space-seperated list of set names to run backups of.""")

# In Windows, Set_Name(s) must be the full path to the set configuration file
# ^ not needed since _users_ don't need to know that. The _system user_ has to
#   know that, but fwbackups takes care of that with pycron internally.

def handleStop(arg1, arg2):
  """ Handles a siging """
  backupHandle.cancelOperation()

# Only if we're in main execution
if __name__ == "__main__":
  verbose = False
  printToo = True
  try:
    avalableOptions = ["help", "verbose", "silent"]
    # letter = plain options
    # letter: = option with arg
    (opts, rest_args) = getopt.gnu_getopt(sys.argv[1:],"hvl", avalableOptions)
  except (getopt.GetoptError), e:
    usage(e)
    sys.exit(1)
  # Remove options from paths
  sets = sys.argv[1:]
  for i in opts:
    for ii in i:
      try:
        sets.remove(ii)
      except:
        pass
  # Parse args, take action
  if opts == []:
    pass
  else:
    for (opt, value) in opts:
      if opt == "-h" or opt == "--help":
        usage()
        sys.exit(1)
      if opt == "-v" or opt == "--verbose":
        verbose = True
      if opt == "-l" or opt == "silent":
        printToo = False
  if not len(sets) >= 1:
    usage(_('Invalid usage: Requires at least one set name to backup'))
    sys.exit(1)
  prefs = config.PrefsConf(create=True)
  if verbose == True or int(prefs.get('Preferences', 'AlwaysShowDebug')) == 1:
    level = fwlogger.L_DEBUG
  else:
    level = fwlogger.L_INFO
  logger = fwlogger.getLogger()
  logger.setLevel(level)
  logger.setPrintToo(printToo)
  # handle ctrl + c
  signal.signal(signal.SIGINT, handleStop)
  for set in sets:
    try:
      if MSWINDOWS:
        set = set.strip('\'')
      backupHandle = backup.SetBackupOperation(os.path.join(SETLOC, "%s.conf" % set), logger=logger)
      backupThread = fwbackups.FuncAsThread(backupHandle.start, {})
    except:
      import traceback
      (etype, evalue, tb) = sys.exc_info()
      tracebackText = ''.join(traceback.format_exception(etype, evalue, tb))
      logger.logmsg('ERROR', _('An error occurred initializing the backup operation:\n%s' % tracebackText))
      sys.exit(1)
    backupThread.start()
    try:
      while backupThread.retval == None:
        time.sleep(0.1)
    except IOError: # ctrl+c raises this on Win32
      print 'IOError while sleep!'

