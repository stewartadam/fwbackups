# -*- coding: utf-8 -*-
#  Copyright (C) 2007, 2008, 2009, 2010 Stewart Adam
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
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA"""
"""
This file contains generic code needed for all of the operations
"""
__all__ = ['backup', 'restore']

import os
import fwbackups
#--
from fwbackups.const import *
from fwbackups.i18n import _, encode

class OperationError(Exception):
  """An Operation error"""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class Common:
  """Base class for all operations"""
  def __init__(self, logger=None, printToo=True):
    """Initializes elements common to all operations. If no logger is specified,
    a new one will be created."""
    # Initialize a logger if none passed
    if not logger:
      from fwbackups import fwlogger
      self.logger = fwlogger.getLogger()
    else:
      self.logger = logger
    # Totals: Nothing so far
    self._status = 0
    self._current = 0
    self._total = 0
    self._currentName = ''
    # No pids to kill, we're not cancelling
    self.pids = []
    self.toCancel = False
    # Execute commands with this environment.
    self.environment = {'PATH': os.getenv('PATH')}

  def cancelOperation(self):
    """Requests the current operation stops as soon as possible"""
    self.logger.logmsg('INFO', _('Canceling the current operation!'))
    if self.pids:
      for process in self.pids:
        try:
          self.logger.logmsg('DEBUG', _('Stopping process with ID %s') % process)
          fwbackups.kill(process, 9)
        except Exception, error:
          self.logger.logmsg('WARNING', _('Could not stop process %(a)s: %(b)s' % (process, error)))
          continue
    self.toCancel = True

  def ifCancel(self, fh=None):
    """Checks if another thread requested the operation be cancelled via
    cancelOperation(). If a file-handle 'fh' is given, it will be closed."""
    if self.toCancel:
      self.logger.logmsg('INFO', _('The operation has been cancelled.'))
      if fh != None:
        fh.close()
      raise SystemExit

  def getProgress(self):
    """Get the progress of the operation. Returns the path number that is
    currently being backed up, the total number of paths and the current file
    name being processed as a list."""
    return [self._status, self._current, self._total, self._currentName]

  def onError(self, func, path, exc_info):
    """Handles errors when performing file operations. May be subclassed."""
    self.logger.logmsg('WARNING', _('Error handling file `%s\'') % path)
    self.logger.logmsg('DEBUG', _('Output:\n%s') % ('func:%s\nexc_info:%s' % (func, exc_info)))

  def prepareDestinationFolder(self, folder, createNonExistant=True):
    """Prepare a destination folder for an operation"""
    if os.path.exists(encode(folder)):
      self.logger.logmsg('DEBUG', _('Destination folder `%s\' exists') % folder)
    # folder doesn't exist; try to create if specified
    elif createNonExistant:
      try:
        os.mkdir(encode(folder), 0755)
        self.logger.logmsg('DEBUG', _("Created destination folder `%s'") % folder)
      except OSError, error:
        self.logger.logmsg('ERROR', _("The destination folder `%(a)s' could not be created: %(b)s") % {'a': folder, 'b': error})
        return False
    # make sure the folder is writable
    if not fwbackups.CheckPerms(folder):
      self.logger.logmsg('WARNING', _("You do not have read and write permissions on the destination `%s' - if you backed up system files, this operation may fail.") % folder)
    return True
