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
Configuration classes for fwbackups
"""
import ConfigParser
import locale
import sys

import fwbackups
from fwbackups.i18n import _, encode, decode
from fwbackups.const import *

class ConfigError(Exception):
  """Errors in the configuration file."""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class ValidationError(Exception):
  """Validation errors in the configuration file."""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

def _setupConf():
  """Setup the configuration directory"""
  for directory in [LOC, SETLOC]:
    if not os.path.exists(encode(directory)):
      try:
        os.mkdir(encode(directory), 0700)
      except OSError, error:
        raise ConfigError(_("Could not create configuration folder `%s':" % error))
        sys.exit(1)
    # Passwords that are base64-encoded are stored, so make sure they are secure
    if LINUX or DARWIN:
      if os.stat(encode(LOC)).st_mode != 16832:
        os.chmod(encode(LOC), 0700)
    if not fwbackups.CheckPerms(directory):
      raise ConfigError(_("You do not have read and write permissions on folder `%s'.") % directory)
      sys.exit(1)

class ConfigFile(ConfigParser.ConfigParser):
  """A more sane implementation of the ConfigParser objects. It commits any
     changes to files immediately, and ensures that write() is not called more
     than once (avoiding duplication of the config file's contents).
     Additionally, read() is called after each write action so what is returned
     by the ConfigParser functions is exactly what is in the file.

     If create is True and the configuration file does not exist, an empty file
     will be created."""
  def __init__(self, conffile, create=False):
    ConfigParser.ConfigParser.__init__(self)
    # Renders options case-sensitive
    ConfigParser.ConfigParser.optionxform = self.optionxform
    # conffile is a unicode string - make sure to encode() when appropriate
    self.__conffile = encode(conffile)
    if create and not os.path.exists(self.__conffile):
      fh = open(self.__conffile, 'w')
      fh.close()
    self.read()

  def optionxform(self, option):
    """This function overrides ConfigParser.optionxorm so that options are case
       sensitive"""
    return str(option)

  def readfp(self, fp, filename=None):
    """Overrides the ConfigParser readfp function to call read()"""
    self.read()

  def read(self):
    """Read and parse the configuration file's data."""
    fh = open(self.__conffile, 'r')
    ConfigParser.ConfigParser.readfp(self, fh)
    fh.close()

  def generateDict(self, sections=None):
    """Dumps the configuration settings into a multi-level dictionary object.
       If sections are specified (as a list), only the dicts for those sections
       will be generated and returned."""
    config = {}
    if not sections:
      sections = self.sections()
    for section in sections:
      config[section] = {}
      for option in self.options(section):
        config[section][option] = self.get(section, option)
    return config

  def importDict(self, dictobject):
    """Imports configuration settings from a multi-level dictionary object"""
    # In the loops, the set() method from parent class ConfigParser should be
    # used to avoid doing many consecutive writes. A final write() operation
    # is performed at the end to commit the changes.
    for section in dictobject.keys():
      if type(dictobject[section]) != dict:
        raise ValueError(_("Key %s of is not a dictionary of options") % section)
      else:
        ConfigParser.ConfigParser.add_section(self, section)
      for option, value in dictobject[section].items():
        if type(value) == unicode:
          value = encode(value)
        ConfigParser.ConfigParser.set(self, section, option, str(value))
    # Write _once_ at the end once all changes are imported
    self.write()

  def write(self):
    """Write the text representation to the configuration file."""
    fh = open(self.__conffile, 'w')
    ConfigParser.ConfigParser.write(self, fh)
    fh.close()

  def get(self, section, option):
    """Returns a Unicode object of the value stored in option of section"""
    value = ConfigParser.ConfigParser.get(self, section, option)
    return decode(value)

  def set(self, section, prop, value):
    """Set a value in a given section and save."""
    ConfigParser.ConfigParser.set(self, section, prop, encode(value))
    self.write()
    return True

  def remove_option(self, sectname, optionname):
    """Remove a property & it's value, then save."""
    ConfigParser.ConfigParser.remove_option(self, sectname, optionname)
    self.write()
    return True

  def add_section(self, sectname):
    """Add a section and save."""
    ConfigParser.ConfigParser.add_section(self, sectname)
    self.write()
    return True

  def remove_section(self, sectname):
    """Remove a section and save."""
    ConfigParser.ConfigParser.remove_section(self, sectname)
    self.write()
    return True



class BackupSetConf:
  """Easy way to read and write a backup set configuration file"""
  def __init__(self, setPath, create=False):
    """Opens the set configuration at setPath and ensures that it is valid.
       If create is True, then a new configuration file will be created."""
    self.setPath = setPath
    self.__config = ConfigFile(setPath, create)

    if not self.__config.sections() and create:
      self.__initialize()
    else:
      # If required, makes changes to the configuration files of previous versions
      self.__import()
    # Validates the configuration according to the current specification
    self.__validate()

  def getSetName(self):
    """Returns the set name being used"""
    setName = os.path.basename(os.path.splitext(encode(self.setPath))[0])
    return decode(setName)

  def __initialize(self):
    """Initializes a basic set configuration file with default values"""
    config = {}
    # Generic settings for all config types fwbackups uses
    config["General"] = {}
    config["General"]["Version"] = fwbackups.__version__
    config["General"]["Type"] = "Set"
    # Empty path section
    config["Paths"] = {}
    # Set default values for backup scheduling (12AM daily)
    config["Times"] = {}
    config["Times"]["Custom"] = False
    config["Times"]["Entry"] = "0 0 * * *"
    # Set default options
    config["Options"] = {}
    config["Options"]["Enabled"] = 1
    config["Options"]["CommandBefore"] = ''
    config["Options"]["CommandAfter"] = ''
    config["Options"]["OldToKeep"] = 1
    config["Options"]["DestinationType"] = "local"
    config["Options"]["Destination"] = USERHOME
    config["Options"]["Recursive"] = 1
    config["Options"]["PkgListsToFile"] = 1
    config["Options"]["DiskInfoToFile"] = 0
    config["Options"]["BackupHidden"] = 1
    config["Options"]["Incremental"] = 0
    config["Options"]["Engine"] = "tar"
    config["Options"]["Sparse"] = 0
    config["Options"]["Nice"] = 0
    config["Options"]["Excludes"] = ""
    config["Options"]["FollowLinks"] = 0
    config["Options"]["RemoteHost"] = ''
    config["Options"]["RemotePort"] = ''
    config["Options"]["RemoteUsername"] = ''
    config["Options"]["RemotePassword"] = ''
    config["Options"]["RemoteFolder"] = ''
    self.__config.importDict(config)

  def __import(self):
    """Import old configurations. Only runs if not current version"""
    try:
      oldVersion = self.__config.get('General', 'Version')
    except: # old config which was non-case sensitive
      oldVersion = self.__config.get('General', 'version')
    # Only if it's a version mismatch should we import...
    # Skip further checks if the configuration file matches the current version
    if fwbackups.__version__ == oldVersion:
      return True
    # The code below is an effective "else". The configuration file is not newer
    # than the current version and it is not equal to the current version, so
    # therefore it is older and an import needs to be done.

    # This lets us do what needs to be done for version X and _above_
    fromHereUp = False
    # --------------------------------------------------------
    # oldest first, newest last in for the order of IF clauses
    # --------------------------------------------------------
    # The cron format changed in beta2 or beta3?
    # sparse, excludes and niceness options added in 1.43.0rc3
    # followlinks option added in 1.43.1
    if oldVersion == '1.43' or oldVersion.startswith('1.43.0') or fromHereUp == True:
      fromHereUp = True
      cron = self.__config.get('Times', 'entry').split(' ')
      tempCron = cron[:5]
      tempCron.append('fwbackups-run')
      self.__config.set('Times', 'entry', ' '.join(tempCron))
      self.__config.set('Options', 'excludes', '')
      self.__config.set('Options', 'nice', 0)
      self.__config.set('Options', 'sparse', 0)
      self.__config.set('Options', 'followlinks', '0')
    # Excludes became newline-separated in 1.43.2
    # Support for remote destinations was added
    # Import in 1.43.1 for followlinks was messed up
    if oldVersion == '1.43.1' or fromHereUp == True:
      fromHereUp = True
      if not self.__config.has_option('Options', 'followlinks'):
        self.__config.set('Options', 'followlinks', 0)
      self.__config.set('Options', 'destinationtype', 'local')
      self.__config.set('Options', 'remotehost', '')
      self.__config.set('Options', 'remoteport', 22)
      self.__config.set('Options', 'remoteusername', '')
      self.__config.set('Options', 'remotepassword', '')
      self.__config.set('Options', 'remotefolder', '')
    # Configuration file option names became case-sensitive in 1.43.2rc1
    # Beta 1 accidentally had version as '1.43.2' and there was no 1.43.2beta2
    # So the '1.43.2' version check below is targeting beta1, not the final.
    # This is why has_option is used before each option rename
    if oldVersion in ['1.43.2beta3', '1.43.2'] or fromHereUp == True:
      fromHereUp = True
      # For each option in each section, the lowercase option is read, written
      # to the case-sensitive equivalent, then the lowercase option is removed
      for option in self.__config.options('Paths'):
        if not self.__config.has_option('Paths', option):
          self.__config.set('Paths', option.title(), self.__config.get('Paths', option))
          self.__config.remove_option('Paths', option.lower())
      for option in ['Version', 'Type']:
        if not self.__config.has_option('General', option):
          self.__config.set('General', option, self.__config.get('General', option.lower()))
          self.__config.remove_option('General', option.lower())
      for option in ['Custom', 'Entry']:
        if not self.__config.has_option('Times', option):
          self.__config.set('Times', option, self.__config.get('Times', option.lower()))
          self.__config.remove_option('Times', option.lower())
      for option in ['Enabled', 'CommandBefore', 'CommandAfter', 'OldToKeep',
                     'DestinationType', 'Destination', 'Recursive',
                     'PkgListsToFile', 'DiskInfoToFile', 'BackupHidden',
                     'Engine', 'Sparse', 'Nice', 'Excludes', 'FollowLinks',
                     'RemoteHost', 'RemotePort', 'RemoteUsername',
                     'RemotePassword', 'RemoteFolder']:
        if not self.__config.has_option('Options', option):
          self.__config.set('Options', option, self.__config.get('Options', option.lower()))
          self.__config.remove_option('Options', option.lower())
    # Incremental backups was added in 1.43.2rc2
    if oldVersion == '1.43.2rc1' or fromHereUp == True:
      fromHereUp = True
      if not self.__config.has_option('Options', 'Incremental'):
        self.__config.set('Options', 'Incremental', 0)
    # Nothing for these versions, but keep doing the below
    if oldVersion in ['1.43.2rc2', '1.43.2rc3'] or fromHereUp == True:
      fromHereUp = True
     # Remote password was obuscated in 1.43.3rc1
    if oldVersion == '1.43.2' or fromHereUp == True:
      fromHereUp = True
      encoded = self.__config.get('Options', 'RemotePassword').encode('base64')
      self.__config.set('Options', 'RemotePassword', encoded)
    # Nothing for these versions, but keep doing the below
    # However, there was a typo ("Sparce" vs "Sparse") in the upgrade procedures
    # of previous versions, leaving a lowercase "sparce" key in the config
    if oldVersion in ['1.43.3rc1', '1.43.3rc2'] or fromHereUp == True:
      fromHereUp = True
      if self.__config.has_option("Options", "sparce"):
        self.__config.remove_option("Options", "sparce")
    if oldVersion in ['1.43.3rc3', '1.43.3rc4', '1.43.3rc5', '1.43.3rc6', '1.43.3'] or fromHereUp == True:
      fromHereUp = True
    # Now that the configuration file been imported, reset the version option
    self.__config.set("General", "Version", fwbackups.__version__)
    return True

  def __validate(self, strictValidation=False):
    """Validates a set configuration file. Ensures all required sections and
       options are present, but does not validate their values."""
    config = self.__config.generateDict()
    def sorted(alist):
      """Sorts a list and returns it"""
      copy = alist
      copy.sort()
      return copy
    # Ensure the configuration sections are present - remember these are sorted
    if sorted(config.keys()) != ["General", "Options", "Paths", "Times"]:
      raise ValidationError(_("Set '%s' failed to pass section validation") % self.getSetName())
    # Ensure the set configuration is really a set configuration file
    if self.__config.get("General", "Type") != "Set":
      raise ValidationError(_("'%(a)s' is not a set configuration file.") % self.setPath)
    # Check that all required values are present
    # Validate General section - remember the list is sorted
    if not sorted(config["General"].keys()) == ["Type", "Version"]:
      raise ValidationError(_("Configuration section 'General' in the set configuration '%s' failed to validate") % self.getSetName())
    # Validate Times section - remember the list is sorted
    if not sorted(config["Times"].keys()) == ["Custom", "Entry"]:
      raise ValidationError(_("Configuration section 'Times' in the set configuration '%s' failed to validate") % self.getSetName())
    # Validate Options section - remember the list is sorted
    validOptions = ['BackupHidden', 'CommandAfter', 'CommandBefore', "Destination",
      'DestinationType', 'DiskInfoToFile', 'Enabled', 'Engine', 'Excludes',
      'FollowLinks', 'Incremental', 'Nice', 'OldToKeep', 'PkgListsToFile',
      'Recursive', 'RemoteFolder', 'RemoteHost', 'RemotePassword', 'RemotePort',
      'RemoteUsername', 'Sparse']
    for option in sorted(config["Options"].keys()):
      if not option in validOptions:
        # This must be placed in a separate if statement, as if it was placed in
        # the above statement when strictValidation=False and an invalid option
        # is present, validOptions.remove(option) is attempted and fails
        if strictValidation:
          raise ValidationError(_("Unknown option key '%(a)s' present in set configuration '%(b)s'") % {'a': option, 'b': self.getSetName()})
      else:
        validOptions.remove(option)
    # If there are any option names left in validOptions, those were missing
    if validOptions:
      raise ValidationError(_("Configuration section 'Options' in set configuration '%(a)s' failed to validate: Missing options '%(b)s'") % {'a': self.getSetName(), 'b': ', '.join(validOptions)})

  def get(self, section, option):
    """Returns value stored in option of section."""
    return self.__config.get(section, option)

  def getPaths(self):
    """Return all the paths, sorted alphabetically, in the set configuration"""
    paths = []
    for pathkey in self.__config.options("Paths"):
      paths.append(self.__config.get("Paths", pathkey))
    paths.sort()
    return paths

  def getOptions(self):
    """Returns a dictionary of all options and their values"""
    config = self.__config.generateDict(sections=["Options"])
    return config["Options"]
  
  def getCronLineText(self):
    """Returns the cron line in text form"""
    try:
      entry = self.__config.get('Times', 'Entry').split(' ')[:5]
      if MSWINDOWS: # needs an abs path because pycron=system user
        entry.append('"%s" "%s\\fwbackups-run.py" -l "%s"' % (sys.executable, INSTALL_DIR, fwbackups.escapeQuotes(self.getSetName(), 2)))
      else:
        entry.append('fwbackups-run -l \'%s\'' % fwbackups.escapeQuotes(self.getSetName(), 1))
      # Add signature to end
      entry.append(CRON_SIGNATURE)
      return entry
    except Exception, error:
      return None

  def save(self, paths, options, times, mergeDefaults=False):
    """Saves a set configuration file from dict-dump objects options and times,
       as well as paths which is a list of paths to backup. The options passed
       in options and times will be validated and if validation fails, the
       previous configuration will be restored and an error is raised. If
       mergeDefaults is True, then the values supplied in paths, options and
       times are merged with the default values."""
    # Backup the current configuration in a dict in case it needs to be restored
    backup = self.__config.generateDict()
    # Remove the current configuration & create a blank one
    os.remove(encode(self.setPath))
    self.__config = ConfigFile(self.setPath, True)
    if mergeDefaults:
      self.__initialize()
    # Generate a new dictionary config dump, then import it
    config = self.__config.generateDict()
    for section in ["General", "Paths", "Options", "Times"]:
      if section not in config.keys():
        config[section] = {}
    config["General"] = {"Type": "Set", "Version": fwbackups.__version__}
    # A loop is used instead of plain assignment in order to maintain expected
    # behavior when mergeDefaults=True
    for option, value in times.items():
      config["Times"][option] = value
    for option, value in options.items():
      config["Options"][option] = value
    paths.sort()
    counter = 0
    for path in paths:
      config["Paths"]["Path%s" % counter] = path
      counter += 1
    self.__config.importDict(config)
    try: # Attempt to validate the file
      self.__validate()
    except: # Restore original backup configuration and raise an error
      os.remove(encode(self.setPath))
      self.__config = ConfigFile(self.setPath, True)
      self.__config.importDict(backup)
      raise



class OneTimeConf:
  """Easy way to read and write a one-time backup configuration file"""
  def __init__(self, onetPath, create=False):
    """Opens the one-time configuration at onetPath and ensures that it is valid.
       If create is True, then a new configuration file will be created,
       overwriting the previous one-time backup configuration."""
    self.onetPath = onetPath
    self.__config = ConfigFile(onetPath, create)

    if not self.__config.sections() or create:
      # Remove existing config if it exists
      if os.path.exists(encode(self.onetPath)):
        os.remove(encode(self.onetPath))
        self.__config = ConfigFile(self.onetPath, True)
      # Initialize the defaults from our now-clean config
      self.__initialize()
    # Validates the configuration according to the current specification
    self.__validate()

  def __initialize(self):
    """Initializes a basic set configuration file with default values"""
    config = {}
    # Generic settings for all config types fwbackups uses
    config["General"] = {}
    config["General"]["Version"] = fwbackups.__version__
    config["General"]["Type"] = "OneTime"
    # Empty path section
    config["Paths"] = {}
    # Set default options
    config["Options"] = {}
    config["Options"]["DestinationType"] = "local"
    config["Options"]["Destination"] = USERHOME
    config["Options"]["Recursive"] = 1
    config["Options"]["PkgListsToFile"] = 1
    config["Options"]["DiskInfoToFile"] = 0
    config["Options"]["BackupHidden"] = 1
    config["Options"]["Incremental"] = 0
    config["Options"]["Engine"] = "tar"
    config["Options"]["Sparse"] = 0
    config["Options"]["Nice"] = 0
    config["Options"]["Excludes"] = ""
    config["Options"]["FollowLinks"] = 0
    config["Options"]["RemoteHost"] = ''
    config["Options"]["RemotePort"] = ''
    config["Options"]["RemoteUsername"] = ''
    config["Options"]["RemotePassword"] = ''
    config["Options"]["RemoteFolder"] = ''
    self.__config.importDict(config)

  def __validate(self, strictValidation=False):
    """Validates a set configuration file. Ensures all required sections and
       options are present, but does not validate their values."""
    config = self.__config.generateDict()
    def sorted(alist):
      """Sorts a list and returns it"""
      copy = alist
      copy.sort()
      return copy
    # Ensure the configuration sections are present - remember these are sorted
    if sorted(config.keys()) != ["General", "Options", "Paths"]:
      raise ValidationError(_("One-time configuration failed to pass section validation"))
    # Ensure the set configuration is really a set configuration file
    if self.__config.get("General", "Type") != "OneTime":
      raise ValidationError(_("'%(a)s' is not a one-time configuration file.") % self.onetPath)
    # Check that all required values are present
    # Validate General section - remember the list is sorted
    if not sorted(config["General"].keys()) == ["Type", "Version"]:
      raise ValidationError(_("Configuration section 'General' in the one-time configuration file failed to validate"))
    # Validate Options section - remember the list is sorted
    validOptions = ['BackupHidden', "Destination", 'DestinationType',
      'DiskInfoToFile', 'Engine', 'Excludes', 'FollowLinks', 'Incremental',
      'Nice', 'PkgListsToFile', 'Recursive', 'RemoteFolder', 'RemoteHost',
      'RemotePassword', 'RemotePort', 'RemoteUsername', 'Sparse']
    for option in sorted(config["Options"].keys()):
      if not option in validOptions:
        # This must be placed in a separate if statement, as if it was placed in
        # the above statement when strictValidation=False and an invalid option
        # is present, validOptions.remove(option) is attempted and fails
        if strictValidation:
          raise ValidationError(_("Unknown option key '%s' present in one-time backup configuration file") % option)
      else:
        validOptions.remove(option)
    # If there are any option names left in validOptions, those were missing
    if validOptions:
      raise ValidationError(_("Configuration section 'Options' in the one-time backup configuration file failed to validate: Missing options '%s'") % ', '.join(validOptions))

  def getPaths(self):
    """Return all the paths, sorted alphabetically, in the set configuration"""
    paths = []
    for pathkey in self.__config.options("Paths"):
      paths.append(self.__config.get("Paths", pathkey))
    paths.sort()
    return paths

  def getOptions(self):
    """Returns a dictionary of all options and their values"""
    config = self.__config.generateDict(sections=["Options"])
    return config["Options"]

  def save(self, paths, options, mergeDefaults=False):
    """Saves a one-time configuration file from dict-dump object options as well
       as paths which is a list of paths to backup. The options passed in
       options will be validated and if validation fails, the previous
       configuration will be restored and an error is raised. If mergeDefaults
       is True, then the values supplied in paths, options are merged with the
       default values."""
    # Backup the current configuration in a dict in case it needs to be restored
    backup = self.__config.generateDict()
    # Remove the current configuration & create a blank one
    os.remove(encode(self.onetPath))
    self.__config = ConfigFile(self.onetPath, True)
    if mergeDefaults:
      self.__initialize()
    # Generate a new dictionary config dump, then import it
    config = self.__config.generateDict()
    for section in ["General", "Paths", "Options"]:
      if section not in config.keys():
        config[section] = {}
    config["General"] = {"Type": "OneTime", "Version": fwbackups.__version__}
    # A loop is used instead of plain assignment in order to maintain expected
    # behavior when mergeDefaults=True
    for option, value in options.items():
      config["Options"][option] = value
    paths.sort()
    counter = 0
    for path in paths:
      config["Paths"]["Path%s" % counter] = path
      counter += 1
    self.__config.importDict(config)
    try: # Attempt to validate the file
      self.__validate()
    except: # Restore original backup configuration and raise an error
      os.remove(encode(self.onetPath))
      self.__config = ConfigFile(self.onetPath, True)
      self.__config.importDict(backup)
      raise


class RestoreConf:
  """Easy way to read and write a restore configuration file"""
  def __init__(self, restorePath, create=False):
    """Opens the restore configuration at restorePath and ensures that it is
       valid. If create is True, then a new configuration file will be created,
       overwriting the previous restore configuration."""
    self.restorePath = restorePath
    self.__config = ConfigFile(restorePath, create)

    if not self.__config.sections() or create:
      # Remove existing config if it exists
      if os.path.exists(encode(self.restorePath)):
        os.remove(encode(self.restorePath))
        self.__config = ConfigFile(self.restorePath, True)
      # Initialize the defaults from our now-clean config
      self.__initialize()
    # Validates the configuration according to the current specification
    self.__validate()

  def __initialize(self):
    """Initializes a basic set configuration file with default values"""
    config = {}
    # Generic settings for all config types fwbackups uses
    config["General"] = {}
    config["General"]["Version"] = fwbackups.__version__
    config["General"]["Type"] = "Restore"
    # Set default options
    config["Options"] = {}
    config["Options"]["SourceType"] = "local"
    config["Options"]["Source"] = USERHOME
    config["Options"]["Destination"] = USERHOME
    config["Options"]["RemoteHost"] = ''
    config["Options"]["RemotePort"] = ''
    config["Options"]["RemoteUsername"] = ''
    config["Options"]["RemotePassword"] = ''
    config["Options"]["RemoteSource"] = ''
    self.__config.importDict(config)

  def __validate(self, strictValidation=False):
    """Validates a set configuration file. Ensures all required sections and
       options are present, but does not validate their values."""
    config = self.__config.generateDict()
    def sorted(alist):
      """Sorts a list and returns it"""
      copy = alist
      copy.sort()
      return copy
    # Ensure the configuration sections are present - remember these are sorted
    if sorted(config.keys()) != ["General", "Options"]:
      raise ValidationError(_("Restore configuration failed to pass section validation"))
    # Ensure the set configuration is really a set configuration file
    if self.__config.get("General", "Type") != "Restore":
      raise ValidationError(_("'%(a)s' is not a restore configuration file.") % self.restorePath)
    # Check that all required values are present
    # Validate General section - remember the list is sorted
    if not sorted(config["General"].keys()) == ["Type", "Version"]:
      raise ValidationError(_("Configuration section 'General' in the restore configuration file failed to validate"))
    # Validate Options section - remember the list is sorted
    validOptions = ['Destination', 'RemoteHost', 'RemotePassword', 'RemotePort',
                    'RemoteSource', 'RemoteUsername', 'Source', 'SourceType']
    for option in sorted(config["Options"].keys()):
      if not option in validOptions:
        # This must be placed in a separate if statement, as if it was placed in
        # the above statement when strictValidation=False and an invalid option
        # is present, validOptions.remove(option) is attempted and fails
        if strictValidation:
          raise ValidationError(_("Unknown option key '%s' present in restore configuration file") % option)
      else:
        validOptions.remove(option)
    # If there are any option names left in validOptions, those were missing
    if validOptions:
      raise ValidationError(_("Configuration section 'Options' in the restore configuration file failed to validate: Missing options '%s'") % ', '.join(validOptions))

  def getOptions(self):
    """Returns a dictionary of all options and their values"""
    config = self.__config.generateDict(sections=["Options"])
    return config["Options"]

  def save(self, options, mergeDefaults=False):
    """Saves a restore configuration file from dict-dump object options. The
       options passed in options will be validated and if validation fails, the
       previous configuration will be restored and an error is raised. If
       mergeDefaults is True, then the values supplied in paths, options are
       merged with the default values."""
    # Backup the current configuration in a dict in case it needs to be restored
    backup = self.__config.generateDict()
    # Remove the current configuration & create a blank one
    os.remove(encode(self.restorePath))
    self.__config = ConfigFile(self.restorePath, True)
    if mergeDefaults:
      self.__initialize()
    # Generate a new dictionary config dump, then import it
    config = self.__config.generateDict()
    for section in ["General", "Options"]:
      if section not in config.keys():
        config[section] = {}
    config["General"] = {"Type": "Restore", "Version": fwbackups.__version__}
    # A loop is used instead of plain assignment in order to maintain expected
    # behavior when mergeDefaults=True
    for option, value in options.items():
      config["Options"][option] = value
    self.__config.importDict(config)
    try: # Attempt to validate the file
      self.__validate()
    except: # Restore original backup configuration and raise an error
      os.remove(encode(self.restorePath))
      self.__config = ConfigFile(self.restorePath, True)
      self.__config.importDict(backup)
      raise

class PrefsConf:
  """Easy way to read and write a preference configuration file"""
  def __init__(self, create=False):
    """Opens the user preferences file (at PREFSLOC) and ensures that it is
       valid. If create is True, then a new configuration file will be created
       if none already exists."""
    self.__config = ConfigFile(PREFSLOC, create)

    if not self.__config.sections() and create:
      self.__initialize()
    else:
      # If required, makes changes to the configuration files of previous versions
      self.__import()
    # Validates the configuration according to the current specification
    self.__validate()

  def __initialize(self):
    """Initializes a basic set configuration file with default values"""
    config = {}
    # Generic settings for all config types fwbackups uses
    config["General"] = {}
    config["General"]["Version"] = fwbackups.__version__
    config["General"]["Type"] = "Preferences"
    # Set default options
    config["Preferences"] = {}
    config["Preferences"]["ShowTrayIcon"] = 1
    config["Preferences"]["MinimizeTrayClose"] = 0
    config["Preferences"]["StartMinimized"] = 0
    config["Preferences"]["ShowNotifications"] = 1
    config["Preferences"]["DontShowMe_OldVerWarn"] = 0
    config["Preferences"]["DontShowMe_ClearLog"] = 0
    pycronLoc = "C:\\Program Files\\pycron"
    if MSWINDOWS:
      try:
        pycronLoc = fwbackups.getPyCronDir()
      except:
        pass
    config["Preferences"]["pycronLoc"] = pycronLoc
    config["Preferences"]["AlwaysShowDebug"] = 0
    self.__config.importDict(config)

  def __validate(self, strictValidation=False):
    """Validates a set configuration file. Ensures all required sections and
       options are present, but does not validate their values."""
    config = self.__config.generateDict()
    def sorted(alist):
      """Sorts a list and returns it"""
      copy = alist
      copy.sort()
      return copy
    # Ensure the configuration sections are present - remember these are sorted
    if sorted(config.keys()) != ["General", "Preferences"]:
      raise ValidationError(_("Preferences failed to pass section validation"))
    # Ensure the set configuration is really a set configuration file
    if self.__config.get("General", "Type") != "Preferences":
      raise ValidationError(_("'%(a)s' is not a fwbackups preferences file.") % PREFSLOC)
    # Check that all required values are present
    # Validate General section - remember the list is sorted
    if not sorted(config["General"].keys()) == ["Type", "Version"]:
      raise ValidationError(_("Configuration section 'General' in the preferences file failed to validate"))
    # Validate Options section - remember the list is sorted
    validOptions = ['AlwaysShowDebug', 'DontShowMe_OldVerWarn',
                    'DontShowMe_ClearLog', 'MinimizeTrayClose', 'pycronLoc',
                    'ShowNotifications', 'ShowTrayIcon', 'StartMinimized']
    for option in sorted(config["Preferences"].keys()):
      if not option in validOptions:
        # This must be placed in a separate if statement, as if it was placed in
        # the above statement when strictValidation=False and an invalid option
        # is present, validOptions.remove(option) is attempted and fails
        if strictValidation:
          raise ValidationError(_("Unknown option key '%s' present in preferences file") % option)
      else:
        validOptions.remove(option)
    # If there are any option names left in validOptions, those were missing
    if validOptions:
      raise ValidationError(_("Configuration section 'Options' in the preferences file failed to validate: Missing options '%s'") % ', '.join(validOptions))

  def __import(self):
    """Import old configurations. Only runs if not current version"""
    try:
      oldVersion = self.__config.get('General', 'Version')
    except: # old config from beta3
      oldVersion = self.__config.get('General', 'version')
    # only if it's a version mismatch should we import
    if oldVersion == fwbackups.__version__:
      return True
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
      self.__config.set('Preferences', 'alwaysshowdebug', 0)
      self.__config.set('Preferences', 'pycronloc', 'C:\\Program Files\\pycron')
      self.__config.set('Preferences', 'dontshowme_netconnectunresponsive', 0)
    # just do the other stuff
    if oldVersion == '1.43.2beta1' or fromHereUp == True:
      fromHereUp = True
    # There was no 1.43.2beta2
    if oldVersion == '1.43.2beta3' or fromHereUp == True:
      fromHereUp = True
      # we forgot to add the 1.43.2beta2 if clause in 1.43.2beta3
      if not self.__config.has_option('Preferences', 'minimizetrayclose'):
        self.__config.set('Preferences', 'minimizetrayclose', 0)
      if not self.__config.has_option('Preferences', 'startminimized'):
        self.__config.set('Preferences', 'startminimized', 0)
      for option in ['Version', 'Type']:
        self.__config.set('General', option, self.__config.get('General', option.lower()))
        self.remove_option('General', option.lower())
      for option in ['ShowTrayIcon', 'MinimizeTrayClose', 'StartMinimized',
                     'ShowNotifications', 'DontShowMe_OldVerWarn',
                     'DontShowMe_ClearLog', 'DontShowMe_NetConnectUnresponsive',
                     'pycronLoc', 'AlwaysShowDebug']:
        self.__config.set('Preferences', option, self.__config.get('Preferences', option.lower()))
        self.remove_option('Preferences', option.lower())
      # --
      self.remove_option('Preferences', 'DontShowMe_NetConnectUnresponsive')
    # just do stuff below
    if oldVersion in ['1.43.2rc1', '1.43.2rc2', '1.43.2rc3', '1.43.2', '1.43.3rc1',
                      '1.43.3rc2', '1.43.3rc3', '1.43.3rc4'] or fromHereUp == True:
      fromHereUp = True
    if oldVersion == '1.43.3rc5' or fromHereUp == True:
      fromHereUp = True
      # In 1.43.3rc5 we added an "# autogenerated" comment to any of the crontab
      # entries fwbackups generates to distinguish them. This removes any
      # fwbackups-related entries for the last time so that new entries can be
      # generated with the comment.
      #
      # This allows us to remove only entries specificially generated by
      # fwbackups, and keep entries with "fwbackups-run" that we did not
      # generate.
      from fwbackups import cron
      cleanedLines = []
      # Read the existing crontab
      crontabLines = cron.read()
      # Parse each line and skip any fwbackup-related ones
      cleanedLines = []
      for line in crontabLines:
        if line.is_comment_or_whitespace():
          # Never clean out comments or whitespace
          cleanedLines.append(line)
        else:
          # if not comment or whitespace, check if the entry is not fwbackups related
          if line.get_raw_entry_text().find('fwbackups-run') == -1:
            cleanedLines.append(line)
      # re-schedule current sets
      files = os.listdir(encode(SETLOC))
      files.sort()
      for file in files:
        if file.endswith('.conf') and file != 'temporary_config.conf':
          print [file]
          try:
            setPath = decode(os.path.join(encode(SETLOC), file))
            setConf = BackupSetConf(setPath)
            entry = setConf.getCronLineText()
            crontabLine = cron.crontabLine(*entry)
            if not crontabLine.is_parsable():
              continue
            cleanedLines.append(crontabLine)
          except Exception, error:
            continue # set or cron entry text is not parsable, just move on
      try: # write cleaned lines
        cron.write(cleanedLines)
      except: # write backup
        cron.write(crontabLines)
        raise
        raise ConfigError(_("Unable to clean user crontab!"))
    if oldVersion in ['1.43.3rc6', '1.43.3'] or fromHereUp == True:
      fromHereUp = True
    
    self.__config.set("General", "Version", fwbackups.__version__)
    return True

  def get(self, section, option):
    """Returns the value of option in section."""
    return self.__config.get(section, option)

  def getboolean(self, section, option):
    """Returns the value of option in section."""
    return self.__config.getboolean(section, option)

  def getPreferences(self):
    """Returns a dictionary of all options and their values"""
    config = self.__config.generateDict(sections=["Preferences"])
    return config["Preferences"]

  def set(self, section, option, value):
    """Sets the value of option in section."""
    return self.__config.set(section, option, value)

  def save(self, options, mergeDefaults=False):
    """Saves a preferences configuration file from dict-dump object options. The
       options passed in options will be validated and if validation fails, the
       previous configuration will be restored and an error is raised. If
       mergeDefaults is True, then the values supplied in paths, options are
       merged with the default values."""
    # Backup the current configuration in a dict in case it needs to be restored
    backup = self.__config.generateDict()
    # Remove the current configuration & create a blank one
    os.remove(encode(PREFSLOC))
    self.__config = ConfigFile(PREFSLOC, True)
    if mergeDefaults:
      self.__initialize()
    # Generate a new dictionary config dump, then import it
    config = self.__config.generateDict()
    for section in ["General", "Preferences"]:
      if section not in config.keys():
        config[section] = {}
    config["General"] = {"Type": "Preferences", "Version": fwbackups.__version__}
    # A loop is used instead of plain assignment in order to maintain expected
    # behavior when mergeDefaults=True
    for option, value in options.items():
      config["Preferences"][option] = value
    self.__config.importDict(config)
    try: # Attempt to validate the file
      self.__validate()
    except: # Restore original backup configuration and raise an error
      os.remove(encode(PREFSLOC))
      self.__config = ConfigFile(PREFSLOC, True)
      self.__config.importDict(backup)
      raise
