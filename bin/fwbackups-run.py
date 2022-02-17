#!/usr/bin/python2
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
import locale
import os
import sys
import time
import getopt
import signal

from fwbackups.i18n import _, encode, decode
from fwbackups.const import *

if sys.platform.startswith('win'):
  sys.path.insert(0, os.path.join(INSTALL_DIR, "pythonmodules"))
  sys.path.insert(1, os.path.join(INSTALL_DIR, "pythonmodules", "gtk-2.0"))

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
  -f, --force :  Run the backup even if the set is disabled.

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
  forceRun = False
  try:
    avalableOptions = ["help", "verbose", "silent", "force"]
    # letter = plain options
    # letter: = option with arg
    (opts, rest_args) = getopt.gnu_getopt(sys.argv[1:],"hvlf", avalableOptions)
  except (getopt.GetoptError), e:
    usage(e)
    sys.exit(1)
  # Remove options from paths
  try: # Pycron passes arguments as UTF-8 encoded bytestrings
    sets = [decode(setPath) for setPath in sys.argv[1:]]
  except UnicodeDecodeError: # Command line passes UTF-8 directly
    sets = [unicode(set, locale.getpreferredencoding()) for set in sys.argv[1:]]
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
      if opt == "-l" or opt == "--silent":
        printToo = False
      if opt == "-f" or opt == "--force":
        forceRun = True
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
  for setPath in sets:
    if MSWINDOWS:
      setPath = setPath.strip("'")
    setPath = os.path.join(SETLOC, "%s.conf" % setPath)
    if not os.path.exists(encode(setPath)):
      logger.logmsg("ERROR", _("The set configuration for '%s' was not found - skipping." % setPath))
      continue
    try:
      backupHandle = backup.SetBackupOperation(setPath, logger=logger, forceRun=forceRun)
      backupThread = fwbackups.FuncAsThread(backupHandle.start, {})
    except Exception, error:
      import traceback
      (etype, evalue, tb) = sys.exc_info()
      tracebackText = ''.join(traceback.format_exception(etype, evalue, tb))
      logger.setPrintToo(True)
      logger.logmsg('WARNING', _("An error occurred while initializing the backup operation!"))
      logger.logmsg('ERROR', tracebackText)
      sys.exit(1)
    backupThread.start()
    try:
      while backupThread.retval == None:
        time.sleep(0.1)
    except IOError: # ctrl+c raises this on Win32
      print 'IOError while sleep!'
    # thread returned
    logger.logmsg('DEBUG', _('Thread returned with retval %s' % backupThread.retval))
    if backupThread.retval == -1:
      logger.logmsg('WARNING', _('There was an error while performing the backup!'))
      logger.logmsg('ERROR', backupThread.traceback)
