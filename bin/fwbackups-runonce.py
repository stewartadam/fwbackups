#!/usr/bin/python
# -*- coding: utf-8 -*-
#  Copyright (C) 2007, 2008, 2009 Stewart Adam
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
import signal
import getopt

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
    print _("""Usage: fwbackups-runonce [OPTIONS] Path(s) Destination
Options:
  -v, --verbose  :  Increase verbosity (print debug messages)
  -h, --help  :  Print this message and exit
  -r, --recursive  :  Perform a recursive backup
  -i, --hidden  :  Include hidden files in the backup
  -p, --packages2file  :  Print installed package list to a text file
  -d, --diskinfo2file  :  Print disk geometry to a file (must be root)
  -s, --sparse  :  Handle sparse files efficiently
  -e, --engine=ENGINE  :  Use specified backup engine.
              Valid engines are tar, tar.gz, tar.bz2 and rsync.
  -x, --exclude='PATTERN'  :  Skip files matching PATTERN.
  -n, --nice=NICE  :  Indicate the niceness of the backup process (-20 to 19)
  --destination-type=TYPE  :  Destination type (`local' or `remote (ssh)')
  --remote-host=HOSTNAME  :  Connect to remote host `HOSTNAME'
  --remote-user=USERNAME  :  Connect as specified username
  --remote-password=PASSWORD  :  Connect using password `PASSWORD'
  --remote-port=PORT  :  Connect on specified port (default 22)

Path(s) is space-seperated list of paths to include in the backup.
Destination is the directory where the OneTime backup should be placed within.

Defaults to tar engine and local destination unless specified otherwise.
Supplying --remote* will have no effect unless thedestination type is
`remote (ssh)'.""")

def handleStop(arg1, arg2):
  """ Handles a siging """
  backupHandle.cancelOperation()

# Only if we're in main execution
if __name__ == "__main__":
  onetime = config.OneTimeConf(True)
  # set the defaults
  onetime.set('Options', 'Recursive', 0)
  onetime.set('Options', 'BackupHidden', 0)
  onetime.set('Options', 'PkgListsToFile', 0)
  onetime.set('Options', 'DiskInfoToFile', 0)
  onetime.set('Options', 'Sparse', 0)
  onetime.set('Options', 'RemotePort', 22)
  onetime.set('Options', 'RemoteUsername', USER)
  verbose = False
  paths = []
  excludes = []
  try:
    avalableOptions = ["help", "verbose", "recursive", "hidden", "sparse",
               "packages2file", "diskinfo2file", "destination-type=",
               "engine=", "exclude=", "nice=", "remote-host=", "remote-username=",
               "remote-port=", "remote-password="]

    # letter = plain options
    # letter: = option with arg
    (opts, rest_args) = getopt.gnu_getopt(sys.argv[1:],"hvripdse:x:n:", avalableOptions)
  except (getopt.GetoptError), e:
    usage(e)
    sys.exit(1)
  # Remove options from paths
  paths = sys.argv[1:]
  for i in opts:
    for ii in i:
      try:
        paths.remove(ii)
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
      if opt == "-r" or opt == "--recursive":
        onetime.set('Options', 'Recursive', 1)
      if opt == "-i" or opt == "--hidden":
        onetime.set('Options', 'Hidden', 1)
      if opt == "-p" or opt == "--packages2file":
        onetime.set('Options', 'PkgListsToFile', 1)
      if opt == "-d" or opt == "--diskinfo2file":
        onetime.set('Options', 'DiskInfoToFile', 1)
      if opt == "-s" or opt == "--sparse":
        onetime.set('Options', 'Sparse', 1)
      if opt == "-e" or opt == "--engine":
        if value in ['tar', 'tar.gz', 'tar.bz2', 'rsync']:
          onetime.set('Options', 'engine', value)
        else:
          usage(_('No such engine `%s\'' % value))
          sys.exit(1)
      if opt == "-x" or opt == "--exclude":
        excludes.append(value)
      if opt == "-n" or opt == "--nice":
        if int(value) >= -20 and int(value) <= 19:
          if UID != 0 and int(value) < 0:
            usage(_('You must be root to set a niceness below 0'))
            sys.exit(1)
          onetime.set('Options', 'Nice', value)
        else:
          usage(_('Nice value must be an integer between -20 and 19'))
          sys.exit(1)
      if opt == "--destination-type":
        onetime.set('Options', 'DestinationType', value)
      if opt == "--remote-host":
        onetime.set('Options', 'RemoteHost', value)
      if opt == "--remote-user":
        onetime.set('Options', 'RemoteUsername', value)
      if opt == "--remote-password":
        onetime.set('Options', 'RemotePassword', value)
      if opt == "--remote-port":
        onetime.set('Options', 'RemotePort', value)
  # handle ctrl + c
  onetime.set('Options', 'Excludes', '\n'.join(excludes))
  signal.signal(signal.SIGINT, handleStop)
  if os.path.exists(ONETIMELOC):
    os.remove(ONETIMELOC)
  if len(paths) < 2:
    usage(_('Invalid usage: Requires at least one path and a destination'))
    sys.exit(1)
  prefs = config.PrefsConf(create=True)
  if verbose == True or int(prefs.get('Preferences', 'AlwaysShowDebug')) == 1:
    level = fwlogger.L_DEBUG
  else:
    level = fwlogger.L_INFO
  logger = fwlogger.getLogger()
  logger.setLevel(level)
  logger.setPrintToo(True)
  # FIXME: Why both? Make RemoteDestination == Destination
  onetime.set('Options', 'Destination', paths[-1])
  onetime.set('Options', 'RemoteFolder', paths[-1])
  pathnumber = 0
  for i in paths[:-1]:
    if MSWINDOWS:
      i = i.strip('\'')
    pathno = 'path' + str(pathnumber)
    onetime.set('Paths', pathno, os.path.abspath(i))
    pathnumber = int(pathnumber + 1)
  try:
    backupHandle = backup.OneTimeBackupOperation(ONETIMELOC, logger=logger)
    backupThread = fwbackups.FuncAsThread(backupHandle.start, {}, raiseOnException=False)
  except:
    import traceback
    (etype, evalue, tb) = sys.exc_info()
    tracebackText = ''.join(traceback.format_exception(etype, evalue, tb))
    logger.logmsg('ERROR', _('An error occurred initializing the backup operation:\n%s' % tracebackText))
    sys.exit(1)
  backupThread.start()
  try:
    while backupThread.isAlive():
      time.sleep(0.1)
  except IOError: # ctrl+c raises this on Win32
    print 'IOError while sleep!'


