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
"""
Python interface to 'crontab' binary
"""

import os
import re
import types

from i18n import _
from const import *

from fwbackups import execute, executeSub
from fwbackups import config

class CronError(Exception):
  """Cron interfacing error."""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

def escape(string, noQuotes):
  """Escapes quotes in string"""
  if noQuotes == 1:
    splitString = "'"
    return ('%s\\%s%s' % (splitString,splitString,splitString)).join(string.split(splitString))
  elif noQuotes == 2:
    splitString = '"'
    return ('\\%s' % splitString).join(string.split(splitString))
  else:
    raise ValueError('noQuotes must be and integer of 1 or 2')
  

class CronLine:
  """A single crontab line"""
  def __init__(self, line):
    """Initialize. @param line can be either list or string."""
    if type(line) == types.ListType:
      split = line
    else:
      split = line.split(' ')
    try:
      if line == '':
        self.isNewline = True
        self.isComment = False
      elif split[0].startswith('#'):
        self.isComment = True
        self.isNewline = False
        self.comment = line
      else:
        self.isComment = False
        self.isNewline = False
        self.minute = split[0]
        self.hour = split[1]
        self.dayOfMonth = split[2]
        self.month = split[3]
        self.dayOfWeek = split[4]
        self.command = ' '.join(split[5:]) + '\n'
    except Exception, error:
      print _('Error while assigning CronLine variables! line:\n`%s\'') % line
      print _('Error: \n%s') % error
      self.isComment = True
      self.isNewline = False
      self.comment = line

  def validate(self):
    """Validate the crontab entry"""
    for i in [self.minute, self.hour, self.dayOfMonth, self.month, self.dayOfWeek]:
      if re.compile("^[0-9/\-,*]*$").search(i) == None:
        index = [self.minute, self.hour, self.dayOfMonth, self.month, self.dayOfWeek].index(i) + 1
        return CronError('Invalid character found in field %i' % index)

  def getEntry(self):
    """Returns the crontab entry as a string"""
    if self.isComment:
      return self.comment + '\n'
    elif self.isNewline:
      return '\n'
    else:
      self.validate()
      return '%s %s %s %s %s %s' % (self.minute, self.hour, self.dayOfMonth, self.month, self.dayOfWeek, self.command)

def getPyCrontab():
  prefConf = config.PrefsConf()
  pycronLoc = prefConf.get('Preferences', 'pycronLoc')
  if os.path.exists('%s/pycron.cfg' % pycronLoc):
    pycronConf = config.ConfigFile('%s/pycron.cfg' % pycronLoc)
  elif os.path.exists('%s/pycron.cfg.sample' % pycronLoc):
    pycronConf = config.ConfigFile('%s/pycron.cfg.sample' % pycronLoc)
  else: # no cron found!
    raise CronError(_('Could not locate the pycron or the sample pycron ' + \
                    'configuration in %s' % pycronLoc))
  crontabName = pycronConf.get('pycron', 'crontab_filename')
  if not os.path.exists('%s\\%s' % (pycronLoc, crontabName)):
    try:
      fh = open('%s\\%s' % (pycronLoc, crontabName), 'w')
      fh.write('# PyCron crontab file\n')
      fh.close()
    except:
      raise CronError(_('Could not locate the pycron or the sample pycron ' + \
                      'crontab file in %s' % pycronLoc))
  return '%s\\%s' % (pycronLoc, crontabName)

class CronTab:
  """The class for in iterfacing with the crontab"""
  def __init__(self):
    """Initialize it all"""
    if LINUX:
      self.environ = {'EDITOR': 'python %s/cronwriter.py' % INSTALL_DIR,
                      'VISUAL': 'python %s/cronwriter.py' % INSTALL_DIR}
    elif DARWIN:
      self.environ = {'EDITOR': '/fwbackups-cronwriter.py',
                      'VISUAL': '/fwbackups-cronwriter.py'}
    else:
      self.environ = {}

  def read(self):
    """Read the crontab"""
    if MSWINDOWS:
      crontabLoc = getPyCrontab()
      fh = open(crontabLoc, 'r')
      toRead = fh
    else:
      sub = executeSub(['crontab', '-l'], self.environ)
      retval = sub.wait(3)
      if retval != os.EX_OK and retval != 1:
        raise CronError('stderr:\n%sstdout:\n%s' % (sub.stderr.readlines(), sub.stdout.readlines()))
      toRead = sub.stdout
    # -- #
    lines = []
    for i in toRead.readlines():
      lines.append(CronLine(i.strip('\n')))
    if MSWINDOWS: # close up
      fh.close()
    return lines

  def clean(self):
    """Rids all fwbackups entries from a user's crontab"""
    lines = self.read()
    if MSWINDOWS:
      crontabLoc = getPyCrontab()
      fh = open(crontabLoc, 'w')
      fh.write('')
      fh.close()
    else:
      sub = executeSub(['crontab', '-r'], self.environ)
    writeBack = []
    for i in lines:
      if i.isComment or i.isNewline:
        writeBack.append(i.getEntry())
        continue
      elif re.compile(".*fwbackups.*").search(i.command) == None:
        writeBack.append(i.getEntry())
    #print 'write', writeBack
    self.write(''.join(writeBack))

  def write(self, content):
    """Overwrite the crontab with @param content"""
    if MSWINDOWS:
      crontabLoc = getPyCrontab()
      fh = open(crontabLoc, 'w')
      fh.write(content)
      fh.close()
    else:
      if DARWIN:
        os.symlink(os.path.join(INSTALL_DIR, 'cronwriter.py'), '/fwbackups-cronwriter.py')
      sub = executeSub(['crontab', '-e'], self.environ)
      sub.stdin.write(content)
      sub.stdin.close()
      retval = sub.wait(3)
      if DARWIN:
        os.remove('/fwbackups-cronwriter.py')
      if retval != os.EX_OK:
        stdout = ' '.join(sub.stdout.readlines())
        stderr = ' '.join(sub.stderr.readlines())
        raise CronError(_('Could not write line `%(a)s\' to crontab:\n%(b)s%(c)s') % {'a': content, 'b': stdout, 'c': stderr})

  def search(self, line):
    """Search for an entry"""
    entry = line.getEntry()
    lines = self.read()
    for i in lines:
      if i.getEntry() == entry:
        return True
    return False

  def add(self, line):
    """Add a crontab entry"""
    lines = self.read()
    lines.append(line)
    contents = ''
    for i in lines:
      contents += i.getEntry()
    self.write(contents)

  def edit(self, oldline, newline):
    """Edit a crontab entry"""
    if not self.remove(oldline):
      raise CronError(_('No matches found for \'%s\'.') % oldline)
    self.add(newline)

  def remove(self, line):
    """Remove a crontab entry"""
    entry = line.getEntry()
    lines = self.read()
    for i in lines: # for each line
      if i.getEntry().strip('\n') == entry: # if we have a match
        lines.remove(i)
        contents = []
        for ii in lines:
          contents.append(ii.getEntry())
        self.write(''.join(contents))
        return True
    return False

