# -*- coding: utf-8 -*-
#  Copyright (C) 2005, 2006, 2007, 2008, 2009, 2010 Stewart Adam
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
The fwbackups logger
"""
import datetime
import logging
import types

from fwbackups.const import *
from fwbackups.i18n import _, encode

L_DEBUG = logging.DEBUG
L_INFO = logging.INFO
L_WARNING = logging.WARNING
L_ERROR = logging.ERROR
L_CRITICAL = logging.CRITICAL
LOGGERS = {'main': 'fwbackups-main'}
LEVELS = {'DEBUG': L_DEBUG,
          'INFO': L_INFO,
          'WARNING': L_WARNING,
          'ERROR': L_ERROR,
          'CRITICAL': L_CRITICAL}

def getLogger():
  """Retrieve the fwbackups logger"""
  logging.setLoggerClass(fwLogger)
  logger = logging.getLogger(LOGGERS['main'])
  # reset to prevent excessive paramiko logging
  logging.setLoggerClass(logging.Logger)
  return logger

def shutdown():
  """Shut down the logging system"""
  logging.shutdown()

class fwLogger(logging.Logger):
  """A subclass to logging.Logger"""
  def __init__(self, name, level=logging.DEBUG):
    """Setup the fwbackups logger, text mode"""
    logging.Logger.__init__(self, name, level)
    self.__printToo = False
    self.__functions = []
    self.__newmessages = False
    try:
      # need a handler
      loghandler = logging.FileHandler(encode(LOGLOC), 'a')
      # Create formatter & add formatter to handler
      logformatter = logging.Formatter("%(message)s")
      loghandler.setFormatter(logformatter)
      # add handler to logger
      self.addHandler(loghandler)
    except Exception as error:
      from fwbackups import fwbackupsError
      raise fwbackupsError(_('Could not set up the logger: %s' % str(error)))

  def setPrintToo(self, printToo):
    """If printToo is True, print messages to stdout as we log them"""
    self.__printToo = printToo

  def getPrintToo(self):
    """Retrieves the printToo property"""
    return self.__printToo

  def unconnect(self, function):
    """Disconnects a function from logmsg. Returns true if disconnected, false
        if that function was not connected."""
    try:
      self.__functions.remove(function)
      return True
    except ValueError:
      return False

  def connect(self, function):
    """Connects a function to logmsg. `function' must be passed as an instance,
        not the function() call itself.

        Function will be given the severity and message as arguments:
        def callback(severity, message)"""
    self.__functions.append(function)

  def logmsg(self, severity, message):
    """Logs a message. Severity is one of 'debug', 'info', 'warning', 'error'
    or 'critical'."""
    date = datetime.datetime.now().strftime('%b %d %H:%M:%S')
    level = self.getEffectiveLevel()
    if level <= LEVELS[severity]:
      entry = '%s :: %s : %s' % (date.decode('utf-8'), _(severity), message)
      self.log(LEVELS[severity], entry.encode('utf-8'))
      if self.__printToo:
        print(entry.encode('utf-8'))
      # pull in & execute the appropriate function
      for i in self.__functions:
        i(severity, entry)
