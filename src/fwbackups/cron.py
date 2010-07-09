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
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
Python interface to 'crontab' binary
"""

import os
import re
import time
import types

from i18n import _
from const import *

from fwbackups import execute, executeSub, kill
from fwbackups import config

class CronError(Exception):
  """Cron interfacing error."""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class ValidationError(Exception):
  """Cron interfacing error."""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class rawCrontabLine:
  """Represents a raw, unparsed line in the crontab"""
  __rawtext = ''
  
  def __init__(self, line):
    """Initialize the raw representation of the line"""
    self.__rawtext = line
  
  def is_comment_or_whitespace(self):
    """Returns True if the crontab entry is a comment"""
    entry_text = self.get_raw_entry_text()
    if not entry_text.strip() or entry_text.lstrip().startswith("#"):
      return True
    return False
  
  def get_raw_entry_text(self):
    """Return the raw text for the entry"""
    return self.__rawtext
  
class crontabLine(rawCrontabLine):
  """Parses an entry in the crontab"""
  # Initialize some variables to their default values
  __minute = None
  __hour = None
  __dayofmonth = None
  __month = None
  __dayofweek = None
  __command = None
  __end_comment = ''
  
  def __init__(self, minute, hour, dayofmonth, month, dayofweek, command, end_comment=''):
    """Parses the crontab entry line constructs the object"""
    self.set_all_fields(minute, hour, dayofmonth, month, dayofweek, command, end_comment)
    rawCrontabLine.__init__(self, self.get_raw_entry_text())
  
  def is_parsable(self):
    """Returns True if the crontab entry is parsable (comments count as parsable)"""
    if not self.is_comment_or_whitespace() \
       and None in [self.__minute, self.__hour, self.__dayofmonth,
                    self.__month, self.__dayofweek, self.__command]:
      return False
    # Basic sanity check on time fields for invalid (ie non-numeric) values
    for field in [self.__minute, self.__hour, self.__dayofmonth, self.__month, self.__dayofweek]:
      if re.compile("^[0-9/\-,*]*$").search(field) == None:
        return False
    return True
  
  def get_all_fields(self):
    """Returns the fields for the crontab entry if the line was parsable.
    Otherwise, returns None."""
    if not self.is_parsable():
      raise ValueError("Entry is not parsable")
    return (self.__minute, self.__hour, self.__dayofmonth, self.__month, self.__dayofweek, self.__command, self.__end_comment)
  
  def set_all_fields(self, minute, hour, dayofmonth, month, dayofweek, command, end_comment=''):
    """Sets all fields in the crontab line"""
    self.__minute, self.__hour, self.__dayofmonth, self.__month, \
    self.__dayofweek, self.__command, self.__end_comment = minute, hour, \
      dayofmonth, month, dayofweek, command, end_comment or ''
    self.__rawtext = self.generate_entry_text()
  
  def validate(self):
    """If the entry was not parsable, a ValueError is raised."""
    if not self.is_parsable() and not self.is_comment_or_whitespace():
      raise ValueError("Entry is not parsable - cannot generate entry text")
  
  def generate_entry_text(self):
    """Return the generated text for the entry."""
    fields = [self.__minute, self.__hour, self.__dayofmonth, self.__month,
              self.__dayofweek, self.__command, self.__end_comment]
    # If we're here then all fields were validated
    return ' '.join(fields).rstrip()+'\n'

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

def getPyCrontab():
  """Read the PyCron crontab file on Windows"""
  prefConf = config.PrefsConf()
  pycronLoc = prefConf.get('Preferences', 'pycronLoc')
  # See if the configuration file exists
  pycronConfig = os.path.join(pycronLoc, 'pycron.cfg')
  if os.path.exists(pycronConfig):
    pycronConf = config.ConfigFile(pycronConfig)
  # If not, does the sample configuation exist?
  elif os.path.exists('%s.sample' % pycronConfig):
    pycronConf = config.ConfigFile('%s.sample' % pycronConfig)
  # No cron file found!
  else:
    raise CronError(_("Could not locate the pycron or the sample pycron configuration in %s" % pycronLoc))
  # Read in the configuration file we found
  pycrontab = os.path.join(pycronLoc, pycronConf.get('pycron', 'crontab_filename'))
  if not os.path.exists(pycrontab):
    try:
      fh = open(pycrontab, 'w')
      fh.write('# PyCron crontab file\n')
      fh.close()
    except:
      raise CronError(_("Could not locate the pycron or the sample pycron crontab file in %s" % pycronLoc))
  return pycrontab

def read():
  """Read in crontab entires from a crontab-formatted file. Returns a list of
  rawCrontabLine objects, one for each line."""
  if MSWINDOWS:
    # Read from pycron's crontab file
    crontabLoc = getPyCrontab()
    fh = open(crontabLoc, 'r')
  else:
    # Read from the user's crontab
    sub = executeSub(['crontab', '-l'])
    retval = sub.wait()
    if retval != os.EX_OK and retval != 1:
      raise CronError('stderr:\n%sstdout:\n%s' % (sub.stderr.readlines(), sub.stdout.readlines()))
    fh = sub.stdout
  # Parse the lines
  lines = [rawCrontabLine(line) for line in fh.readlines()]
  if MSWINDOWS:
    fh.close()
  return lines

def write(crontabEntries=[]):
  """Write a crontab-formatted file from the list of fstabLines. Return values
  of 0 or 1 to indicate a failure writing to the crontab or a success
  respectively."""
  if LINUX:
    environ = {'EDITOR': 'python %s/cronwriter.py' % INSTALL_DIR,
               'VISUAL': 'python %s/cronwriter.py' % INSTALL_DIR}
  elif DARWIN:
    environ = {'EDITOR': '/fwbackups-cronwriter.py',
               'VISUAL': '/fwbackups-cronwriter.py'}
  else:
    environ = {}
  remove()
  try:
    if MSWINDOWS:
      crontab = getPyCrontab()
      fh = open(crontab, 'w')
    else:
      if DARWIN:
        if os.path.islink('/fwbackups-cronwriter.py'):
          os.remove('/fwbackups-cronwriter.py')
        os.symlink(os.path.join(INSTALL_DIR, 'cronwriter.py'), '/fwbackups-cronwriter.py')
      sub = executeSub(['crontab', '-e'], environ)
      fh = sub.stdin
    # Write the content to the crontab
    for crontabEntry in crontabEntries:
      if isinstance(crontabEntry, crontabLine): # generate the entry text
        fh.write(crontabEntry.generate_entry_text())
      else:
        fh.write(crontabEntry.get_raw_entry_text())
    time.sleep(1)
    fh.close()
    if not MSWINDOWS:
      counter = 0.0
      while sub.poll() in [None, ""] and counter < 5.0: # After waiting for 5 seconds, assume that the crontab could not be installed
        time.sleep(0.1)
        counter += 0.1
      if sub.poll() in [None, ""]:
        # Soft-terminate the process if it still hasn't finished
        kill(sub.pid, 15)
        sub.wait()
        raise ValidationError(_("The crontab could not be saved"))
      if DARWIN:
        os.remove('/fwbackups-cronwriter.py')
      if sub.poll() != os.EX_OK:
        stdout = ' '.join(sub.stdout.readlines())
        stderr = ' '.join(sub.stderr.readlines())
        raise CronError(_('Could not write new crontab:\n%(a)s%(b)s') % {'a': stdout, 'b': stderr})
    fh.close()
  except IOError: # can't open crontab file
    return 0
  return 1

def remove():
  """Removes/empties a user's crontab"""
  if MSWINDOWS:
    crontab = getPyCrontab()
    fh = open(crontab, 'w')
    fh.write('')
    fh.close()
  else:
    sub, stdout, stderr = execute(['crontab', '-r'])

def clean_fwbackups_entries():
  """Reads the crontab and removes any fwbackups entries. Returns the cleaned
  lines as crontabLine objects. Does not write any changes to the crontab."""
  # Read the existing crontab
  crontabLines = read()
  # Parse each line and skip any fwbackup-related ones
  cleanedLines = []
  for line in crontabLines:
    if line.is_comment_or_whitespace():
      # Never clean out comments or whitespace
      cleanedLines.append(line)
    else:
      # if not comment or whitespace, try to parse it and see if it has our signature
      rawtext = line.get_raw_entry_text()
      match = re.match(r"^([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+(.+?)\s*(#.*)?$", rawtext.strip())
      if match == None:
        continue
      parsedLine = crontabLine(*match.groups())
      fields = parsedLine.get_all_fields()
      if not (fields[5].startswith('fwbackups-run') and fields[6].startswith(CRON_SIGNATURE)):
        cleanedLines.append(line)
  return cleanedLines
    
