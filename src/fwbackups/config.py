# -*- coding: utf-8 -*-
#  Copyright (C) 2005 - 2009 Stewart Adam
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
Configuration classes for fwbackups
"""
import ConfigParser
import sys

import fwbackups
from fwbackups.i18n import _
from fwbackups.const import *

class ConfigError(Exception):
  """Errors in the configuration file."""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

def _setupConf():
  """Setup the configuration directory"""
  for i in [LOC, SETLOC]:
    if not os.path.exists(i):
      try:
        os.mkdir(i, 0755)
      except OSError, error:
        raise ConfigError(_("Could not create configuration folder `%s':" % error))
        sys.exit(1)
    if not fwbackups.CheckPerms(i):
      raise ConfigError(_("You do not have read and write permissions on folder `%s'.") % i)
      sys.exit(1)

class ConfigFile(ConfigParser.ConfigParser):
  """A more sane ConfigParser. It commits changes immediately, and also
  re-parses after each action so what-you-see-is-what's-in-the-file."""
  # Basic setup.
  def __init__(self, conffile, create=False, logger=None):
    ConfigParser.ConfigParser.__init__(self)
    ConfigParser.ConfigParser.optionxform = self.optionxform
    self.config = ConfigParser.ConfigParser()
    self.conffile = conffile
    if not logger:
      self.logger = None
    else:
      self.logger = logger
    # Finally...
    self.read(create)

  def optionxform(self, option):
    """Case sensitive!"""
    return str(option)

  def set_conffile(self, conffile, create=False):
    """Use a new config file at 'conffile', recreating it if create=True"""
    self.conffile = conffile
    self.read(create)

  def get_conffile(self):
    """Returns the config file path."""
    return self.conffile

  def read(self, create=False):
    """Read & parse the config file."""
    #self.logger.logmsg('DEBUG', _('Reading configuration file \'%s\'') % self.conffile)
    if create == True and not os.path.exists(self.conffile):
      #self.logger.logmsg('DEBUG', _('Creating new configuration file \'%s\'') % self.conffile)
      self.fh = open(self.conffile,'w')
      self.fh.write('')
      self.fh.close()
    elif create == False and not os.path.exists(self.conffile):
      raise ConfigError(_('Attempted to read non-existant file \'%s\'') % self.conffile)
    self.fh = open(self.conffile,'r')
    self.config.readfp(self.fh)
    self.fh.close()

  def write(self):
    """Write the config file, then reparse."""
    try:
      #self.logger.logmsg('DEBUG', _('Writing configuration file \'%s\'') % self.conffile)
      self.fh = open(self.conffile,'w')
      self.config.write(self.fh)
      self.fh.close()
      self.read()
    except:
      raise ConfigError(_('Cannot write to file \'%s\'') % self.conffile)

  def set(self, section, prop, value):
    """Set a value in a given section and save."""
    self.config.set(section, prop, value)
    self.write()
    return True

  def get(self, section, prop):
    """Returns the value for a given option in a section"""
    value = self.config.get(section, prop)
    return value

  def getboolean(self, section, prop):
    """Returns the value for a given option in a section"""
    value = self.config.getboolean(section, prop)
    return value

  def remove_option(self, sectname, optionname):
    """Remove a property & it's value, then save."""
    self.config.remove_option(sectname, optionname)
    self.write()
    return True

  def add_section(self, sectname):
    """Add a section and save."""
    self.config.add_section(sectname)
    self.write()
    return True

  def remove_section(self, sectname):
    """Remove a section and save."""
    self.config.remove_section(sectname)
    self.write()
    return True

  def sections(self):
    """Returns the sections in the file"""
    return self.config.sections()

  def options(self, section):
    """Returns the options in a section of the file"""
    return self.config.options(section)

  def has_section(self, section):
    """Has section x?"""
    return self.config.has_section(section)

  def has_option(self, section, option):
    """Has option x in section y?"""
    return self.config.has_option(section, option)

class BackupSetConf(ConfigFile):
  """Backup set configuration file"""
  def __init__(self, setName, create=False, logger=None):
    """Checks for previous versions, incomplete confs, etc"""
    #if os.path.exists(setName): # check for full path
    #  self.setName = '.conf'.join(os.path.basename(setName).split('.conf')[:-1]) #  setName = full path
    #  self.setPath = setName
    #else:
    #  self.setName = setName
    #  self.setPath = ConvertPath('%s/%s.conf' % (SETLOC, self.setName))
    self.setName = setName
    self.setPath = ConvertPath('%s/%s.conf' % (SETLOC, self.setName))
    ConfigFile.__init__(self, self.setPath, create, logger)
    if self.sections() == [] and create == True:
      self._setupBasicConf()

    for i in ['General', 'Paths', 'Options', 'Times']:
      if not self.has_section(i):
        raise ConfigError(_('Set \'%(a)s\' is missing section \'%(b)s\'!') % {'a': setName, 'b': i})
    self._import()
    if self.get('General', 'Type') != 'Set':
      raise ConfigError(_('\'%(a)s\' isn\'t a set configuration file: Its type is set to \'%(b)s\'.') %\
        {'a': self.setName, 'b': self.get('General', 'Type')})

  def getSetName(self):
    """Retruns the set name being used"""
    return self.setName
    
  def _setupBasicConf(self):
    """Creates a basic set configuration file"""
    self.add_section('General')
    self.set('General', 'Version', fwbackups.__version__)
    self.set('General', 'Type', 'Set')
    self.add_section('Paths')
    self.add_section('Options')
    self.add_section('Times')
    self.set('Times', 'Custom','False')
    self.set('Times', 'Entry', '0 0 * * *')
    self.set('Options', 'Enabled', 1)
    self.set('Options', 'CommandBefore', '')
    self.set('Options', 'CommandAfter', '')
    self.set('Options', 'OldToKeep', 1)
    self.set('Options', 'DestinationType', 'local')
    self.set('Options', 'Destination', USERHOME)
    self.set('Options', 'Recursive', 1)
    self.set('Options', 'PkgListsToFile', 1)
    self.set('Options', 'DiskInfoToFile', 0)
    self.set('Options', 'BackupHidden', 1)
    self.set('Options', 'Incremental', '0')
    self.set('Options', 'Engine', 'tar')
    self.set('Options', 'Sparse', 0)
    self.set('Options', 'Nice', 0)
    self.set('Options', 'Excludes', '')
    self.set('Options', 'FollowLinks', '0')
    self.set('Options', 'RemoteHost', '')
    self.set('Options', 'RemotePort', '')
    self.set('Options', 'RemoteUsername', '')
    self.set('Options', 'RemotePassword', '')
    self.set('Options', 'RemoteFolder', '')
    #self.logger.logmsg('DEBUG', _('Setting defaults in configuration file for set \'%s\'') % self.setName)

  def _import(self):
    """Import old configurations. Only runs if not current version"""
    try:
      oldVersion = self.get('General', 'Version')
    except: # old config from beta3
      oldVersion = self.get('General', 'version')
    
    # only if it's a version mismatch should we import
    if oldVersion == fwbackups.__version__:
      self.set('General', 'Version', fwbackups.__version__)
      return True

    # This lets us do what needs to be done for version X and _above_
    fromHereUp = False

    # --------------------------------------------------------
    # oldest first, newest last in for the order of IF clauses
    # --------------------------------------------------------

    # I had changed the cron format in the .conf file in beta2/3? Don't remember
    if oldVersion == '1.43' or oldVersion.startswith('1.43.0') or fromHereUp == True:
      fromHereUp = True
      cron = self.get('Times', 'entry').split(' ')
      tempCron = cron[:5]
      tempCron.append('fwbackups-run')
      self.set('Times', 'entry', ' '.join(tempCron))
      
    # Just so we do the below
    if oldVersion.startswith('1.43.0beta') or oldVersion == '1.43.0rc1' or fromHereUp == True:
      fromHereUp = True
    
    # I added sparse & nice & excludes in 1.43.0rc3
    if oldVersion == '1.43.0rc2' or fromHereUp == True:
      fromHereUp = True
      self.set('Options', 'excludes', '')
      self.set('Options', 'nice', 0)
      self.set('Options', 'sparce', 0)

    # Just so we do the below
    if oldVersion == '1.43.0rc3' or fromHereUp == True:
      fromHereUp = True

    # I added follow links in 1.43.1
    if oldVersion == '1.43.0' or fromHereUp == True:
      fromHereUp = True
      self.set('Options', 'followlinks', '0')

    # excludes became newline-separated in 1.43.2
    # I messed up the import in 1.43.1 for followlinks
    if oldVersion == '1.43.1' or fromHereUp == True:
      fromHereUp = True
      found = False
      for i in self.options('Options'):
        if i == 'followlinks':
          found = True
      if not found:
        self.set('Options', 'followlinks', '0')
      self.set('Options', 'destinationtype', 'local')
      self.set('Options', 'remotehost', '')
      self.set('Options', 'remoteport', '22')
      self.set('Options', 'remoteusername', '')
      self.set('Options', 'remotepassword', '')
      self.set('Options', 'remotefolder', '')
      
    # Just so we do the below
    if oldVersion == '1.43.2beta1' or oldVersion == '1.43.2beta1' or fromHereUp == True:
      fromHereUp = True
      
    # I made the option files case-sensitive in 1.43.2rc1
    if oldVersion == '1.43.2beta3' or fromHereUp == True:
      fromHereUp = True
      for option in self.options('Paths'):
        if not self.has_option('Paths', option):
          self.set('Paths', option.title(), self.get('Paths', option))
          self.remove_option('Paths', option.lower())
      for option in ['Version', 'Type']:
        if not self.has_option('General', option):
          self.set('General', option, self.get('General', option.lower()))
          self.remove_option('General', option.lower())
      for option in ['Custom', 'Entry']:
        if not self.has_option('Times', option):
          self.set('Times', option, self.get('Times', option.lower()))
          self.remove_option('Times', option.lower())
      for option in ['Enabled', 'CommandBefore', 'CommandAfter', 'OldToKeep', 
                     'DestinationType', 'Destination', 'Recursive', 
                     'PkgListsToFile', 'DiskInfoToFile', 'BackupHidden', 
                     'Engine', 'Sparse', 'Nice', 'Excludes', 'FollowLinks', 
                     'RemoteHost', 'RemotePort', 'RemoteUsername', 
                     'RemotePassword', 'RemoteFolder']:
        if not self.has_option('Options', option):
          self.set('Options', option, self.get('Options', option.lower()))
          self.remove_option('Options', option.lower())
        
    if oldVersion == '1.43.2rc1' or fromHereUp == True:
      fromHereUp = True
      self.set('Options', 'Incremental', '0')
    
    # just do stuff below
    if oldVersion in ['1.43.2rc2', '1.43.2rc3'] or fromHereUp == True:
      fromHereUp = True
    if oldVersion == '1.43.2' or fromHereUp == True:
      fromHereUp = True
      encoded = self.get('Options', 'RemotePassword').encode('base64')
      self.set('Options', 'RemotePassword', encoded)
    if oldVersion == '1.43.3rc1' or fromHereUp == True:
      fromHereUp = True
      
    self.set('General', 'Version', fwbackups.__version__)
    return True

class OneTimeConf(ConfigFile):
  """One-Time backup configuration file"""
  def __init__(self, create=False, logger=None):
    """Checks for previous versions, incomplete confs, etc"""
    if create == True and os.path.exists(ONETIMELOC):
      os.remove(ONETIMELOC)
    ConfigFile.__init__(self, ONETIMELOC, create, logger)
    if self.sections() == [] and create == True:
      self._setupBasicConf()
    for i in ['General', 'Paths', 'Options']:
      if not self.has_section(i):
        raise ConfigError(_('Set \'%(a)s\' is missing section \'%(b)s\'!' % {'a': ONETIMELOC, 'b': i}))
    if self.get('General', 'Type') != 'OneTime':
      raise ConfigError(_('\'%(a)s\' isn\'t a one-time configuration file: Its type is set to \'%(b)s\'.') % \
        {'a': ONETIMELOC, 'b': self.get('General', 'Type')})

  def _setupBasicConf(self):
    """Creates a basic onetime configuration file"""
    self.add_section('General')
    self.set('General', 'Type', 'OneTime')
    self.add_section('Paths')
    self.add_section('Options')
    self.set('Options', 'DestinationType', 'local')
    self.set('Options', 'Destination', USERHOME)
    self.set('Options', 'Recursive', 1)
    self.set('Options', 'PkgListsToFile', 1)
    self.set('Options', 'DiskInfoToFile', 0)
    self.set('Options', 'BackupHidden', 1)
    self.set('Options', 'Engine', 'tar')
    self.set('Options', 'Sparse', '0')
    self.set('Options', 'Nice', '0')
    self.set('Options', 'Excludes', '')
    self.set('Options', 'FollowLinks', '0')
    self.set('Options', 'RemoteHost', '')
    self.set('Options', 'RemotePort', '22')
    self.set('Options', 'RemoteUsername', '')
    self.set('Options', 'RemotePassword', '')
    self.set('Options', 'RemoteFolder', '')
    self.set('Options', 'Destination', USERHOME)
    self.set('Options', 'Recursive', 1)

    
class RestoreConf(ConfigFile):
  """Restore configuration file"""
  def __init__(self, create=False, logger=None):
    """Checks for previous versions, incomplete confs, etc"""
    if create == True and os.path.exists(RESTORELOC):
      os.remove(RESTORELOC)
    ConfigFile.__init__(self, RESTORELOC, create, logger)
    if self.sections() == [] and create == True:
      self._setupBasicConf()
    for i in ['General', 'Options']:
      if not self.has_section(i):
        raise ConfigError(_('Set \'%(a)s\' is missing section \'%(b)s\'!' % {'a': RESTORELOC, 'b': i}))
    if self.get('General', 'Type') != 'Restore':
      raise ConfigError(_('\'%(a)s\' isn\'t a restore configuration file: Its type is set to \'%(b)s\'.') % \
        {'a': RESTORELOC, 'b': self.get('General', 'Type')})

  def _setupBasicConf(self):
    """Creates a basic onetime configuration file"""
    self.add_section('General')
    self.set('General', 'Type', 'Restore')
    self.add_section('Options')
    self.set('Options', 'SourceType', 'local')
    self.set('Options', 'RemoteHost', '')
    self.set('Options', 'RemotePort', '22')
    self.set('Options', 'RemoteUsername', '')
    self.set('Options', 'RemotePassword', '')
    self.set('Options', 'RemoteSource', '')
    self.set('Options', 'Source', USERHOME)
    self.set('Options', 'Destination', USERHOME)

class PrefsConf(ConfigFile):
  """Preferences configuration file"""
  def __init__(self, create=False, logger=None):
    """Checks for previous versions, incomplete confs, etc"""
    ConfigFile.__init__(self, PREFSLOC, create, logger)
    if self.sections() == [] and create == True:
      self._setupBasicConf()

    for i in ['General', 'Preferences']:
      if not self.has_section(i):
        raise ConfigError(_('Preference configuration is missing section \'%(a)s\'!') % {'a': i})
    self._import()
    if self.get('General', 'Type') != 'Preferences':
      raise ConfigError(_('\'%(a)s\' isn\'t a preference configuration file: Its type is set to \'%(b)s\'.') %\
        {'a': PREFSLOC, 'b': self.get('General', 'Type')})

  def _setupBasicConf(self):
    """Creates a basic preference configuration file"""
    self.add_section('General')
    self.set('General', 'Version', fwbackups.__version__)
    self.set('General', 'Type', 'Preferences')
    self.add_section('Preferences')
    self.set('Preferences', 'ShowTrayIcon', 1)
    self.set('Preferences', 'MinimizeTrayClose', 0)
    self.set('Preferences', 'StartMinimized', 0)
    self.set('Preferences', 'ShowNotifications', 1)
    self.set('Preferences', 'DontShowMe_OldVerWarn', 0)
    self.set('Preferences', 'DontShowMe_ClearLog', 0)
    try:
      self.set('Preferences', 'pycronLoc', fwbackups.getPyCronDir())
    except:
      self.set('Preferences', 'pycronLoc', 'C:\\Program Files\\pycron')
    self.set('Preferences', 'AlwaysShowDebug', 0)
    #self.logger.logmsg('DEBUG', _('Setting defaults in preferences configuration file'))

  def _import(self):
    """Import old configurations. Only runs if not current version"""
    try:
      oldVersion = self.get('General', 'Version')
    except: # old config from beta3
      oldVersion = self.get('General', 'version')
    # only if it's a version mismatch should we import
    if oldVersion == fwbackups.__version__:
      return True
    elif fwbackups.isNewer(oldVersion, fwbackups.__version__):
      # don't support downgrades
      raise ConfigError(_('The installed configuration is from a newer version of fwbackups - downgrade unsupported'))

    # This lets us do what needs to be done for version X and _above_
    
    fromHereUp = False

    # just make it add stuff from next
    # remember, preferences first started in 1.43.0 final
    if oldVersion == '1.43.0' or fromHereUp == True:
      fromHereUp = True
      
    # I added log verbosity overrides, pycron support (win32), network warning
    # (don't show me) in 1.43.2beta1
    if oldVersion == '1.43.1' or fromHereUp == True:
      fromHereUp = True
      self.set('Preferences', 'alwaysshowdebug', 0)
      self.set('Preferences', 'pycronloc', 'C:\\Program Files\\pycron')
      self.set('Preferences', 'dontshowme_netconnectunresponsive', 0)
    
    # just do the other stuff
    if oldVersion == '1.43.2beta1' or fromHereUp == True:
      fromHereUp = True
    
    # removed network warning since we do threading now
    # made config case-sensitive
    if oldVersion == '1.43.2beta2' or fromHereUp == True:
      self.set('Preferences', 'minimizetrayclose', 0)
      self.set('Preferences', 'startminimized', 0)
    if oldVersion == '1.43.2beta3' or fromHereUp == True:
      # we forgot to add the 1.43.2beta2 if clause in 1.43.2beta3
      if not self.has_option('Preferences', 'minimizetrayclose'):
        self.set('Preferences', 'minimizetrayclose', 0)
      if not self.has_option('Preferences', 'startminimized'):
        self.set('Preferences', 'startminimized', 0)
      fromHereUp = True
      for option in ['Version', 'Type']:
        self.set('General', option, self.get('General', option.lower()))
        self.remove_option('General', option.lower())
      for option in ['ShowTrayIcon', 'MinimizeTrayClose', 'StartMinimized',
                     'ShowNotifications', 'DontShowMe_OldVerWarn',
                     'DontShowMe_ClearLog', 'DontShowMe_NetConnectUnresponsive',
                     'pycronLoc', 'AlwaysShowDebug']:
        self.set('Preferences', option, self.get('Preferences', option.lower()))
        self.remove_option('Preferences', option.lower())
      # --
      self.remove_option('Preferences', 'DontShowMe_NetConnectUnresponsive')
    
    # just do stuff below
    if oldVersion in ['1.43.2rc1', '1.43.2rc2', '1.43.2rc3', '1.43.2', '1.43.3rc1'] or fromHereUp == True:
      fromHereUp = True
    
    return self.set('General', 'Version', fwbackups.__version__)


