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
This file contains the logic for the backup operation
"""
import exceptions
import os
import re
import tempfile
import time
#--
import fwbackups
from fwbackups.i18n import _, encode
from fwbackups.const import *
from fwbackups import config
from fwbackups import operations
from fwbackups import shutil_modded
from fwbackups import sftp

if not MSWINDOWS:
  import fcntl

STATUS_INITIALIZING = 0
STATUS_CLEANING_OLD = 1
STATUS_BACKING_UP = 2
STATUS_SENDING_TO_REMOTE = 3
STATUS_EXECING_USER_COMMAND = 4

class BackupOperation(operations.Common):
  """A parent class for all backups operations."""
  def __init__(self, logger=None):
    """Initalizes the class. If no logger is specified, a new one will be
    created."""
    operations.Common.__init__(self, logger)

  def getOptions(self, conf):
    """Loads all the configuration options from a restore configuration file and
    returns them in a dictionary"""
    def _bool(value):
      return value in [1, '1', True, 'True']
    options = conf.getOptions()
    if not options['RemotePort']:
      options['RemotePort'] = 22
    else:
      options['RemotePort'] = int(options['RemotePort'])
    options['Nice'] = int(options['Nice'])
    options['RemotePassword'] = options['RemotePassword'].decode('base64')
    for option in ['Recursive', 'PkgListsToFile', 'DiskInfoToFile',
                   'BackupHidden', 'FollowLinks', 'Sparse']:
      options[option] = _bool(options[option])
    return options
  
  def escapePath(self, path):
    """Wrap the supplied path in quotes for command line, and escape any other
    single quotes. Returns an 8-bit string."""
    path = path.replace("'", "'\\''")
    return path
  
  def parsePaths(self, config):
    """Get the list of paths in the configuration file. Returns a list of paths to backup"""
    paths = []
    for path in config.getPaths():
      paths.append(path)
    return paths
  
  def createPkgLists(self):
    """Create the pkg lists in tempdir"""
    # Start as a dictionary so we can keep track of which items we have already
    # processed. See comment at retur for more info.
    pkgListFiles = {}
    for path in os.environ['PATH'].split(':'):
      if os.path.exists(os.path.join(path, 'rpm')) and not pkgListFiles.has_key('rpm'):
        fd, path = tempfile.mkstemp(suffix='.txt', prefix="%s - tmp" % _('rpm - Package list'))
        fh = os.fdopen(fd, "w")
        # try with rpm-python, but if not just execute it like the rest
        try:
          import rpm
          pyrpm = True
        except ImportError:
          pyrpm = False
        if pyrpm:
          ts=rpm.ts()
          # Equivalent to rpm -qa
          mi=ts.dbMatch()
          for hdr in mi:
            fh.write("%s-%s-%s.%s\n" % (hdr['name'], hdr['version'], hdr['release'], hdr['arch']))
        else:
          retval, stdout, stderr = fwbackups.execute('rpm -qa', env=self.environment, shell=True, stdoutfd=fh)
        pkgListFiles['rpm'] = path
        fh.close()
      if os.path.exists(os.path.join(path, 'pacman')) and not pkgListFiles.has_key('pacman'):
        fd, path = tempfile.mkstemp(suffix='.txt', prefix="%s - tmp" % _('Pacman - Package list'))
        fh = os.fdopen(fd, 'w')
        retval, stdout, stderr = fwbackups.execute('pacman -Qq', env=self.environment, shell=True, stdoutfd=fh)
        pkgListFiles['pacman'] = path
        fh.close()
      if os.path.exists(os.path.join(path, 'dpkg')) and not pkgListFiles.has_key('dpkg'):
        fd, path = tempfile.mkstemp(suffix='.txt', prefix="%s - tmp" % _('dpkg - Package list'))
        fh = os.fdopen(fd, 'w')
        retval, stdout, stderr = fwbackups.execute('dpkg -l', env=self.environment, shell=True, stdoutfd=fh)
        pkgListFiles['dpkg'] = path
        fh.close()
    # We want to return a list of only the filenames
    return pkgListFiles.values()
  
  def createDiskInfo(self):
    """Print disk info to a file in tempdir"""
    fd, path = tempfile.mkstemp(suffix='.txt', prefix="%s - tmp" % _('Disk Information'))
    fh = os.fdopen(fd, 'w')
    retval, stdout, stderr = fwbackups.execute('fdisk -l', env=self.environment, shell=True, stdoutfd=fh)
    fh.close()
    return fh.name

  def parseCommand(self, config):
    """Parse options to retrieve the correct command"""
    self.options = self.getOptions(self.config)
    if self.options['DestinationType'] == 'remote (ssh)':
      tempDir = tempfile.gettempdir()
      self.dest = os.path.join(tempDir, os.path.split(self.escapePath(self.dest))[1])
    if self.options['Engine'] == 'rsync':
      command = 'rsync -g -o -p -t -R'
      if self.options['Incremental']:
        command += ' -u --del'
      if self.options['Recursive']:
        command += ' -r'
      if not self.options['BackupHidden']:
        command += ' --exclude=.*'
      if self.options['Sparse']:
        command += ' -S'
      if self.options['FollowLinks']:
        command += ' -L'
      else:
        command += ' -l'
      if self.options['Excludes'] != None and self.options['Excludes'] != "":
        for i in self.options['Excludes'].split('\n'):
          command += ' --exclude="%s"' % i
    elif self.options['Engine'] == 'tar':
      command = "tar rf '%s'" % self.escapePath(self.dest)
    elif self.options['Engine'] == 'tar.gz':
      # DON'T rfz - Can't use r (append) and z (gzip) together
      command = "tar cfz '%s'" % self.escapePath(self.dest)
    elif self.options['Engine'] == 'tar.bz2':
      # DON'T rfz - Can't use r (append) and j (bzip2) together
      command = "tar cfj '%s'" % self.escapePath(self.dest)
    # --
    if self.options['Engine'] in ['tar', 'tar.gz', 'tar.bz2']: # they share command options
      if not self.options['Recursive']:
        command += ' --no-recursion'
      if not self.options['BackupHidden']:
        command += ' --exclude=.*'
      if self.options['Sparse']:
        command += ' -S'
      if self.options['FollowLinks']:
        command += ' -h'
    if self.options['Excludes']:
      for i in self.options['Excludes'].split('\n'):
        command += ' --exclude="%s"' % i
    # Finally...
    return command

  def addListFilesToBackup(self, pkgListfiles, command, engine, paths):
    """Adds the pkglist and diskinfo to the backup"""
    self.ifCancel()
    for file in pkgListfiles:
      paths.append(file)

  def deleteListFiles(self, pkgListfiles):
    """Delete the list files in the tempdir"""
    self.ifCancel()
    for file in pkgListfiles:
      os.remove(file)
  
  def checkRemoteServer(self):
    """Checks if a connection to the remote server can be established"""
    self.logger.logmsg('DEBUG', _('Attempting to connect to server %s...') % self.options['RemoteHost'])
    thread = fwbackups.runFuncAsThread(sftp.testConnection,
                                       self.options['RemoteHost'], self.options['RemoteUsername'],
                                       self.options['RemotePassword'], self.options['RemotePort'],
                                       self.options['RemoteFolder'])
    while thread.retval == None:
      time.sleep(0.1)
    # Check for errors, if any
    import paramiko
    import socket
    if thread.retval == True:
      self.logger.logmsg('DEBUG', _('Attempt to connect succeeded.'))
      return True
    elif type(thread.exception) == IOError:
      self.logger.logmsg('ERROR', _('The backup destination was either not ' + \
                     'found or it cannot be written to due to insufficient permissions.'))
      return False
    elif type(thread.exception) == paramiko.AuthenticationException:
      self.logger.logmsg('ERROR', _('A connection was established, but authentication ' + \
                      'failed. Please verify the username and password ' + \
                      'and try again.'))
      return False
    elif type(thread.exception) == socket.gaierror or type(thread.exception) == socket.error:
      self.logger.logmsg('ERROR', _('A connection to the server could not be established.\n' + \
                      'Error %(a)s: %(b)s' % {'a': type(thread.exception), 'b': str(thread.exception)} + \
                      '\nPlease verify your settings and try again.'))
      return False
    elif type(thread.exception) == socket.timeout:
      self.logger.logmsg('ERROR', _('A connection to the server has timed out. ' + \
                      'Please verify your settings and try again.'))
      return False
    elif type(thread.exception) == paramiko.SSHException:
      self.logger.logmsg('ERROR', _('A connection to the server could not be established ' + \
                      'because an error occurred: %s' % str(thread.exception) + \
                      '\nPlease verify your settings and try again.'))
      return False
    else: # not remote, just pass
      return True
  
  def backupPaths(self, paths, command):
    """Does the actual copying dirty work"""
    # this is in common
    self._current = 0
    if len(paths) == 0:
      return True
    self._total = len(paths)
    self._status = STATUS_BACKING_UP
    wasAnError = False
    if self.options['Engine'] == 'tar':
      if MSWINDOWS:
        self.logger.logmsg('INFO', _('Using %s on Windows: Cancel function will only take effect after a path has been completed.' % self.options['Engine']))
        import tarfile
        fh = tarfile.open(self.dest, 'w')
        for i in paths:
          self.ifCancel()
          self._current += 1
          self.logger.logmsg('DEBUG', _('Backing up path %(a)i/%(b)i: %(c)s' % {'a': self._current, 'b': self._total, 'c': i}))
          fh.add(i, recursive=self.options['Recursive'])
        fh.close()
      else: # not MSWINDOWS
        for i in paths:
          i = self.escapePath(i)
          self.ifCancel()
          self._current += 1
          self.logger.logmsg('DEBUG', _("Running command: nice -n %(a)i %(b)s '%(c)s'" % {'a': self.options['Nice'], 'b': command, 'c': i}))
          sub = fwbackups.executeSub("nice -n %i %s '%s'" % (self.options['Nice'], command, i), env=self.environment, shell=True)
          self.pids.append(sub.pid)
          self.logger.logmsg('DEBUG', _('Starting subprocess with PID %s') % sub.pid)
          # track stdout
          errors = []
          # use nonblocking I/O
          fl = fcntl.fcntl(sub.stderr, fcntl.F_GETFL)
          fcntl.fcntl(sub.stderr, fcntl.F_SETFL, fl | os.O_NONBLOCK)
          while sub.poll() in ["", None]:
            time.sleep(0.01)
            try:
              errors += sub.stderr.readline()
            except IOError, description:
              pass
          self.pids.remove(sub.pid)
          retval = sub.poll()
          self.logger.logmsg('DEBUG', _('Subprocess with PID %(a)s exited with status %(b)s' % {'a': sub.pid, 'b': retval}))
          # Something wrong?
          if retval != EXIT_STATUS_OK and retval != 2:
            wasAnError = True
            self.logger.logmsg('ERROR', 'An error occurred while backing up path \'%s\'.\nPlease check the error output below to determine if any files are incomplete or missing.' % str(i))
            self.logger.logmsg('ERROR', _('Process exited with status %(a)s. Errors: %(b)s' % {'a': retval, 'b': ''.join(errors)}))
      
    elif self.options['Engine'] == 'tar.gz':
      self._total = 1
      if MSWINDOWS:
        self.logger.logmsg('INFO', _('Using %s on Windows: Cancel function will only take effect after a path has been completed.' % self.options['Engine']))
        import tarfile
        fh = tarfile.open(self.dest, 'w:gz')
        for i in paths:
          self._current += 1
          self.ifCancel()
          self.logger.logmsg('DEBUG', _('Backing up path %(a)i/%(b)i: %(c)s' % {'a': self._current, 'b': self._total, 'c': i}))
          fh.add(i, recursive=self.options['Recursive'])
          self.logger.logmsg('DEBUG', _('Adding path `%s\' to the archive' % i))
        fh.close()
      else: # not MSWINDOWS
        self._current = 1
        escapedPaths = [self.escapePath(i) for i in paths]
        # This is a fancy way for getting i = "'one' 'two' 'three'"
        i = "'%s'" % "' '".join(escapedPaths)
        self.logger.logmsg('INFO', _('Using %s: Must backup all paths at once - Progress notification will be disabled.' % self.options['Engine']))
        self.logger.logmsg('DEBUG', _('Backing up path %(a)i/%(b)i: %(c)s') % {'a': self._current, 'b': self._total, 'c': i.replace("'", '')})
        self.logger.logmsg('DEBUG', _("Running command: nice -n %(a)i %(b)s %(c)s" % {'a': self.options['Nice'], 'b': command, 'c': i}))
        sub = fwbackups.executeSub("nice -n %i %s %s" % (self.options['Nice'], command, i), env=self.environment, shell=True)
        self.pids.append(sub.pid)
        self.logger.logmsg('DEBUG', _('Starting subprocess with PID %s') % sub.pid)
        # track stdout
        errors = []
        # use nonblocking I/O
        fl = fcntl.fcntl(sub.stderr, fcntl.F_GETFL)
        fcntl.fcntl(sub.stderr, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        while sub.poll() in ["", None]:
          time.sleep(0.01)
          try:
            errors += sub.stderr.readline()
          except IOError, description:
            pass
        self.pids.remove(sub.pid)
        retval = sub.poll()
        self.logger.logmsg('DEBUG', _('Subprocess with PID %(a)s exited with status %(b)s' % {'a': sub.pid, 'b': retval}))
        # Something wrong?
        if retval != EXIT_STATUS_OK and retval != 2:
          wasAnError = True
          self.logger.logmsg('ERROR', 'An error occurred while backing up path \'%s\'.\nPlease check the error output below to determine if any files are incomplete or missing.' % str(i))
          self.logger.logmsg('ERROR', _('Process exited with status %(a)s. Errors: %(b)s' % {'a': retval, 'b': ''.join(errors)}))
          
    elif self.options['Engine'] == 'tar.bz2':
      self._total = 1
      if MSWINDOWS:
        self.logger.logmsg('INFO', _('Using %s on Windows: Cancel function will only take effect after a path has been completed.' % self.options['Engine']))
        import tarfile
        fh = tarfile.open(self.dest, 'w:bz2')
        for i in paths:
          self._current += 1
          self.ifCancel()
          self.logger.logmsg('DEBUG', _('Backing up path %(a)i/%(b)i: %(c)s' % {'a': self._current, 'b': self._total, 'c': i}))
          fh.add(i, recursive=self.options['Recursive'])
          self.logger.logmsg('DEBUG', _('Adding path `%s\' to the archive' % i))
        fh.close()
      else: # not MSWINDOWS
        self._current = 1
        escapedPaths = [self.escapePath(i) for i in paths]
        # This is a fancy way for getting i = "'one' 'two' 'three'"
        i = "'%s'" % "' '".join(escapedPaths)
        self.logger.logmsg('INFO', _('Using %s: Must backup all paths at once - Progress notification will be disabled.' % self.options['Engine']))
        self.logger.logmsg('DEBUG', _('Backing up path %(a)i/%(b)i: %(c)s') % {'a': self._current, 'b': self._total, 'c': i})
        self.logger.logmsg('DEBUG', _("Running command: nice -n %(a)i %(b)s %(c)s" % {'a': self.options['Nice'], 'b': command, 'c': i}))
        sub = fwbackups.executeSub("nice -n %i %s '%s'" % (self.options['Nice'], command, i), env=self.environment, shell=True)
        self.pids.append(sub.pid)
        self.logger.logmsg('DEBUG', _('Starting subprocess with PID %s') % sub.pid)
        # track stdout
        errors = []
        # use nonblocking I/O
        fl = fcntl.fcntl(sub.stderr, fcntl.F_GETFL)
        fcntl.fcntl(sub.stderr, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        while sub.poll() in ["", None]:
          time.sleep(0.01)
          try:
            errors += sub.stderr.readline()
          except IOError, description:
            pass
        self.pids.remove(sub.pid)
        retval = sub.poll()
        self.logger.logmsg('DEBUG', _('Subprocess with PID %(a)s exited with status %(b)s' % {'a': sub.pid, 'b': retval}))
        # Something wrong?
        if retval != EXIT_STATUS_OK and retval != 2:
          wasAnError = True
          self.logger.logmsg('ERROR', 'An error occurred while backing up path \'%s\'.\nPlease check the error output below to determine if any files are incomplete or missing.' % str(i))
          self.logger.logmsg('ERROR', _('Process exited with status %(a)s. Errors: %(b)s' % {'a': retval, 'b': ''.join(errors)}))
    
    elif self.options['Engine'] == 'rsync':
      # in this case, self.{folderdest,dest} both need to be created
      if self.options['DestinationType'] == 'remote (ssh)':
        client, sftpClient = sftp.connect(self.options['RemoteHost'], self.options['RemoteUsername'], self.options['RemotePassword'], self.options['RemotePort'])
        if not wasAnError:
          for i in paths:
            if self.toCancel:
              # Check if we need to cancel in between paths
              # If so, break and close the SFTP session
              # Immediately after, self.ifCancel() is run.
              break
            self._current += 1
            self.logger.logmsg('DEBUG', _('Backing up path %(a)i/%(b)i: %(c)s') % {'a': self._current, 'b': self._total, 'c': i})
            if not os.path.exists(encode(i)):
              self.logger.logmsg('WARNING', _("Path %s is missing or cannot be read and will be excluded from the backup.") % i)
            sftp.put(sftpClient, encode(i), encode(os.path.normpath(self.options['RemoteFolder']+os.sep+os.path.basename(self.dest)+os.sep+os.path.dirname(i))), symlinks=not self.options['FollowLinks'], excludes=encode(self.options['Excludes'].split('\n')))
        sftpClient.close()
        client.close()
      else: # destination is local
        for i in paths:
          self.ifCancel()
          self._current += 1
          if MSWINDOWS:
            # let's deal with real paths
            self.logger.logmsg('DEBUG', _('Backing up path %(a)i/%(b)i: %(c)s' % {'a': self._current, 'b': self._total, 'c': i}))
            shutil_modded.copytree_fullpaths(encode(i), encode(self.dest))
          else: # not MSWINDOWS; UNIX/OS X can call rsync binary
            i = self.escapePath(i)
            self.logger.logmsg('DEBUG', _("Running command: nice -n %(a)i %(b)s %(c)s '%(d)s'" % {'a': self.options['Nice'], 'b': command, 'c': i, 'd': self.escapePath(self.dest)}))
            sub = fwbackups.executeSub("nice -n %i %s '%s' '%s'" % (self.options['Nice'], command, i, self.escapePath(self.dest)), env=self.environment, shell=True)
            self.pids.append(sub.pid)
            self.logger.logmsg('DEBUG', _('Starting subprocess with PID %s') % sub.pid)
            # track stdout
            errors = []
            # use nonblocking I/O
            fl = fcntl.fcntl(sub.stderr, fcntl.F_GETFL)
            fcntl.fcntl(sub.stderr, fcntl.F_SETFL, fl | os.O_NONBLOCK)
            while sub.poll() in ["", None]:
              time.sleep(0.01)
              try:
                errors += sub.stderr.readline()
              except IOError, description:
                pass
            self.pids.remove(sub.pid)
            retval = sub.poll()
            self.logger.logmsg('DEBUG', _('Subprocess with PID %(a)s exited with status %(b)s' % {'a': sub.pid, 'b': retval}))
            # Something wrong?
            if retval not in [EXIT_STATUS_OK, 2]:
              wasAnError = True
              self.logger.logmsg('ERROR', 'An error occurred while backing up path \'%s\'.\nPlease check the error output below to determine if any files are incomplete or missing.' % str(i))
              self.logger.logmsg('ERROR', _('Process exited with status %(a)s. Errors: %(b)s' % {'a': retval, 'b': ''.join(errors)}))
    
    self.ifCancel()
    # A test is included to ensure sure the archive actually exists, as if
    # wasAnError = True the archive might not even exist.
    if self.options['Engine'].startswith('tar') and self.options['DestinationType'] == 'remote (ssh)' and os.path.exists(encode(self.dest)):
      self.logger.logmsg('DEBUG', _('Sending files to server via SFTP'))
      self._status = STATUS_SENDING_TO_REMOTE
      client, sftpClient = sftp.connect(self.options['RemoteHost'], self.options['RemoteUsername'], self.options['RemotePassword'], self.options['RemotePort'])
      try:
        sftp.putFile(sftpClient, self.dest, self.options['RemoteFolder'])
        os.remove(self.dest)
      except:
        import sys
        import traceback
        wasAnError = True
        self.logger.logmsg('DEBUG', _('Could not send file(s) or folder to server:'))
        (etype, value, tb) = sys.exc_info()
        self.logger.logmsg('DEBUG', ''.join(traceback.format_exception(etype, value, tb)))
      sftpClient.close()
      client.close()
    
    # finally, we do this
    self._current = self._total
    time.sleep(1)
    self.ifCancel()
    return (not wasAnError)
  
  def start(self):
    """This must be subclassed"""
    raise NotImplementedError(_('This function is designed to be subclassed'))

######################
######################
class OneTimeBackupOperation(BackupOperation):
  def __init__(self, onetPath, logger=None):
    """Initializes a one-time backup operation. If no logger is specified, a new one
    will be created. logger will be created if needed."""
    BackupOperation.__init__(self, logger)
    self.logger.logmsg('INFO', _('Starting one-time backup operation'))
    self.config = config.OneTimeConf(onetPath)
    self.options = self.getOptions(self.config)
    # Parse backup folder format
    date = time.strftime('%Y-%m-%d_%H-%M')
    self.dest = os.path.join(self.options['Destination'], "%s-%s-%s" % (_('Backup'), _('OneTime'), date))
    # IF tar || tar.gz, add .tar || tar.gz respectively to the dest since
    # the dest is to be a file, not a folder...
    if self.options['Engine'] == 'tar':
      self.dest += '.tar'
    elif self.options['Engine'] == 'tar.gz':
      self.dest += '.tar.gz'
    elif self.options['Engine'] == 'tar.bz2':
      self.dest += '.tar.bz2'

  def start(self):
    """One-time backup"""
    paths = self.parsePaths(self.config)
    if not paths:
      self.logger.logmsg('WARNING', _('There are no paths to backup!'))
      return False
      
    if self.options['DestinationType'] == 'remote (ssh)': # check if server settings are OK
      self.checkRemoteServer()
    
    if self.options['PkgListsToFile']:
      pkgListfiles = self.createPkgLists()
    else:
      pkgListfiles = []
    if self.options['DiskInfoToFile']:
      pkgListfiles.append(self.createDiskInfo())

    if not (self.options['Engine'] == 'rsync' and self.options['Incremental'] and \
       not self.options['DestinationType'] == 'remote (ssh)'):
      if not self.prepareDestinationFolder(self.options['Destination']):
        return False
      if os.path.exists(encode(self.dest)):
        self.logger.logmsg('WARNING', _('`%s\' exists and will be overwritten.') % self.dest)
        shutil_modded.rmtree(encode(self.dest), onerror=self.onError)
    self.ifCancel()

    command = self.parseCommand(self.config)
    self.addListFilesToBackup(pkgListfiles, command, self.options['Engine'], paths)

    # Now that the paths & commands are set up...
    retval = self.backupPaths(paths, command)

    self.deleteListFiles(pkgListfiles)
    self.ifCancel()

    if self.options['DestinationType'] == 'local':
      try:
        os.chmod(self.dest, 0711)
      except:
        pass

    # All done!
    self.logger.logmsg('INFO', _('Finished one-time backup'))
    return retval

######################
######################
class SetBackupOperation(BackupOperation):
  """Automated set backup operation"""
  def __init__(self, setPath, logger=None):
    """Initializes the automatic backup operation of set defined at setPath.
    If no logger is supplied, a new one will be created."""
    BackupOperation.__init__(self, logger)
    self.config = config.BackupSetConf(setPath)
    self.options = self.getOptions(self.config)
    if self.options['Enabled']:
      self.logger.logmsg('INFO', _('Starting automatic backup operation of set `%s\'') % self.config.getSetName())
    # Parse backup folder format
    # date stored as class variable due to re-use in user commands later
    self.date = time.strftime('%Y-%m-%d_%H-%M')
    self.dest = os.path.join(self.options['Destination'], u"%s-%s-%s" % (_('Backup'), self.config.getSetName(), self.date))
    # set-specific options
    # IF tar || tar.gz, add .tar || tar.gz respectively to the dest since
    # the dest is to be a file, not a folder...
    if self.options['Engine'] == 'tar':
      self.dest += '.tar'
    elif self.options['Engine'] == 'tar.gz':
      self.dest += '.tar.gz'
    elif self.options['Engine'] == 'tar.bz2':
      self.dest += '.tar.bz2'
  
  def getOptions(self, config):
    """Subclass getOptions to handle options only in Set configs"""
    def _bool(value):
      return value in [1, '1', True, 'True']
    options = BackupOperation.getOptions(self, config)
    options['Enabled'] = int(options['Enabled'])
    options['Incremental'] = _bool(options['Incremental'])
    options['OldToKeep'] = int(float(options['OldToKeep']))
    return options
  
  def tokens_replace(self, text, date, successful=None):
    """Replace tokens in the supplied text"""
    tokens = {'backup': os.path.basename(encode(self.dest)),
              'set': self.config.getSetName(),
              'date': date,
              'remote_host': self.options['RemoteHost'],
              'remote_username': self.options['RemoteUsername'],
              'remote_password': self.options['RemotePassword'],
              'remote_port': str(self.options['RemotePort']),
             }
    # Only create the success token if we explicitly set to True/False
    if successful != None:
      if successful:
        tokens['successful'] = 1
      else:
        tokens['successful'] = 0
    # Adjust destination folder for remote backups
    if self.options['DestinationType'] == 'remote (ssh)':
      tokens['destination'] = self.options['Destination']
    else:
      tokens['destination'] = self.options['RemoteFolder']
    
    def replace_match(m):
      """Replace non-escaped tokens with values at the beginning of a string"""
      return r"%s" % tokens[m.group(1)]
    
    def replace_match_escape(m):
      """Replace non-escaped tokens with values after the beginning of a string"""
      return r"%s%s" % (m.group(1), tokens[m.group(2)])
    
    for token, sub in tokens.items():
      text = re.sub(r"^\[(%s)\]" % token, replace_match, text)
      text = re.sub(r"([^\\]+?)\[(%s)\]" % token, replace_match_escape, text)
      # Replace escaped tokens into their non-escaped form
      text = text.replace(r"\[%s]" % token, "[%s]" % token)
    return text
  
  def execute_user_command(self, cmd_type, command):
    """Run the after user command"""
    # Before or after command?
    if cmd_type == 1:
      cmd_type_str = 'Before'
    elif cmd_type == 2:
      cmd_type_str = 'After'
    else:
      raise ValueError('Unknown command type value "%s"' % cmd_type)
    # Execute the command
    self.logger.logmsg('INFO', _("Executing '%s' command") % cmd_type_str)
    sub = fwbackups.executeSub(command, env=self.environment, shell=True)
    self.pids.append(sub.pid)
    self.logger.logmsg('DEBUG', _('Starting subprocess with PID %s') % sub.pid)
    # track stdout
    errors = []
    # use nonblocking I/O
    fl = fcntl.fcntl(sub.stderr, fcntl.F_GETFL)
    fcntl.fcntl(sub.stderr, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    while sub.poll() in ["", None]:
      time.sleep(0.01)
      try:
        errors += sub.stderr.readline()
      except IOError, description:
        pass
    self.pids.remove(sub.pid)
    retval = sub.poll()
    # Something wrong?
    if retval != EXIT_STATUS_OK:
      self.logger.logmsg('ERROR', _('Command returned with a non-zero exit status!'))
      self.logger.logmsg('ERROR', _('Process exited with status %(a)s. Errors: %(b)s' % {'a': retval, 'b': ''.join(errors)}))
  
  def removeOldBackups(self):
    """Get list of old backups and remove them"""
    # get listing, local or remote
    if self.options['DestinationType'] == 'remote (ssh)':
      client, sftpClient = sftp.connect(self.options['RemoteHost'], self.options['RemoteUsername'], self.options['RemotePassword'], self.options['RemotePort'])
      listing = sftpClient.listdir(self.options['RemoteFolder'])
    else:
      listing = os.listdir(encode(self.options['Destination']))
    listing.sort()
    oldbackups = []
    for i in listing:
      if i.startswith(u'%s-%s-' % (_('Backup'), self.config.getSetName())):
        oldbackups.append(i)
    # ...And remove them.
    oldbackups.reverse()
    if self.options['DestinationType'] == 'remote (ssh)':
      for i in oldbackups[self.options['OldToKeep']:]:
        remoteBackup = os.path.join(self.options['RemoteFolder'], i)
        self.logger.logmsg('DEBUG', _('Removing old backup `%(a)s\' on %(b)s') % {'a': remoteBackup, 'b': self.options['RemoteHost']})
        sftp.remove(sftpClient, remoteBackup)
      sftpClient.close()
      client.close()
    else:
      if self.options['Engine'] == 'rsync' and self.options['Incremental'] and oldbackups:
        for i in oldbackups[:-1]:
          self.logger.logmsg('DEBUG', _('Removing old backup `%s\'') % i)
          path = os.path.join(self.options['Destination'], i)
          shutil_modded.rmtree(encode(path), onerror=self.onError)
        oldIncrementalBackup = encode(os.path.join(self.options['Destination'], oldbackups[-1]))
        if not oldIncrementalBackup.endswith('.tar') and not oldIncrementalBackup.endswith('.tar.gz') and \
            not oldIncrementalBackup.endswith('.tar.bz2'): # oldIncrementalBackup = rsync
          self.logger.logmsg('DEBUG', _('Moving  `%s\' to `%s\'') % (oldIncrementalBackup, self.dest))
          shutil_modded.move(oldIncrementalBackup, self.dest)
        else: # source = is not a rsync backup - remove it and start fresh
          self.logger.logmsg('DEBUG', _('`%s\' is not an rsync backup - removing.') % oldIncrementalBackup)
          shutil_modded.rmtree(oldIncrementalBackup, onerror=self.onError)
      else:
        for i in oldbackups[self.options['OldToKeep']:]:
          self.logger.logmsg('DEBUG', _('Removing old backup `%s\'') % i)
          path = os.path.join(self.options['Destination'], i)
          shutil_modded.rmtree(encode(path), onerror=self.onError)

  def start(self):
    """Start the backup process. Should be called after executing user command."""
    if self.options['Enabled'] == '0': # set is disabled
      return True
    
    if self.options["CommandBefore"]:
      self._status = STATUS_EXECING_USER_COMMAND
      # Find tokens and substitute them
      tokenized_command = self.tokens_replace(self.options["CommandBefore"], self.date)
      self.execute_user_command(1, tokenized_command)
    
    try:
      # Get the list of paths...
      paths = self.parsePaths(self.config)
      if not paths:
        self.logger.logmsg('WARNING', _('There are no paths to backup!'))
        return False
      
      self.ifCancel()
      
      if self.options['DestinationType'] == 'remote (ssh)': # check if server settings are OK
        self.checkRemoteServer()
      
      self._status = STATUS_CLEANING_OLD
      if not (self.options['Engine'] == 'rsync' and self.options['Incremental']) and \
          not self.options['DestinationType'] == 'remote (ssh)':
        if not self.prepareDestinationFolder(self.options['Destination']):
          return False
        if not (self.options['Engine'] == 'rsync' and self.options['Incremental']) \
        and os.path.exists(encode(self.dest)):
          self.logger.logmsg('WARNING', _('`%s\' exists and will be overwritten.') % self.dest)
          shutil_modded.rmtree(encode(self.dest), onerror=self.onError)
      self.ifCancel()
      
      # Remove old stuff
      self.removeOldBackups()
      self.ifCancel()
      
      self._status = STATUS_INITIALIZING
      if self.options['PkgListsToFile']:
        pkgListfiles = self.createPkgLists()
      else:
        pkgListfiles = []
      if self.options['DiskInfoToFile']:
        pkgListfiles.append(self.createDiskInfo())
      self.ifCancel()
      command = self.parseCommand(self.config)
      self.addListFilesToBackup(pkgListfiles, command, self.options['Engine'], paths)
      # Now that the paths & commands are set up...
      retval = self.backupPaths(paths, command)
      self.deleteListFiles(pkgListfiles)
      if self.options['DestinationType'] == 'local':
        try:
          os.chmod(self.dest, 0711)
        except:
          pass
    # Exception handlers in FuncAsThread() must return retval same values
    except exceptions.SystemExit:
      # cancelled; the only time we skip the after command
      return -2
    except:
      retval = False
      import traceback
      (etype, value, tb) = sys.exc_info()
      self.traceback = ''.join(traceback.format_exception(etype, value, tb))
      self.logger.logmsg('WARNING', _('There was an error while performing the backup!'))
      self.logger.logmsg('ERROR', self.traceback)
      # just incase we have leftover stuff running
      self.cancelOperation()
    
    if self.options["CommandAfter"]:
      self._status = STATUS_EXECING_USER_COMMAND
      # Find tokens and substitute them
      tokenized_command = self.tokens_replace(self.options["CommandAfter"], self.date, retval)
      self.execute_user_command(2, tokenized_command)
    
    # All done!
    self.logger.logmsg('INFO', _("Finished automatic backup operation of set '%s'") % self.config.getSetName())
    return retval
