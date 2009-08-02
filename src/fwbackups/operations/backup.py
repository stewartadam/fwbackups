# -*- coding: utf-8 -*-
#  Copyright (C) 2007 - 2009 Stewart Adam
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
import os
import tempfile
import time
#--
import fwbackups
from fwbackups.i18n import _
from fwbackups.const import *
from fwbackups import config
from fwbackups import operations
from fwbackups import shutil_modded
from fwbackups import sftp

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

  def parsePaths(self, config):
    """Get the list of paths in the configuration file. Returns a list of paths to backup"""
    paths = []
    for path in config.getPaths():
      # non recursive - Skip dirs
      if self.options['Recursive'] == False and os.path.isdir(path):
        continue # move on to next file
      paths.append("'%s'" % '\'\\\'\''.join(path.split('\''))) # wrap it in quotes for command line, and escape other single quote
    if paths == []:
      self.logger.logmsg('WARNING', _('After parsing options, there are no paths to backup!') + ' paths == []')
      return False, -1
    return paths

  def createPkgLists(self):
    """Create the pkg lists in tempdir"""
    managers = []
    for path in os.environ['PATH'].split(':'):
      if os.path.exists(os.path.join(path, 'rpm')) and not 'rpm' in managers:
        # try with rpm-python, but if not just execute it like the rest
        try:
          import rpm
          pyrpm = True
        except ImportError:
          pyrpm = False
        if pyrpm:
          listFilename = os.path.join(tempfile.gettempdir(), '%s.txt' % _('rpm - Package list'))
          listFile = open(listFilename, 'w')
          ts=rpm.ts()
          # Equivalent to rpm -qa
          mi=ts.dbMatch()
          for hdr in mi:
            listFile.write("%s-%s-%s.%s\n" % (hdr['name'], hdr['version'], hdr['release'], hdr['arch']))
          listFile.close()
        else:
          outfile = os.path.join(tempfile.gettempdir(), '%s.txt' % _('rpm - Package list'))
          retval, stdout, stderr = fwbackups.execute('rpm -qa', env=self.environment, shell=True, stdoutfd=open(outfile, 'w'))
          stdout.close()
        managers.append('rpm')
      if os.path.exists(os.path.join(path, 'pacman')) and not 'pacman' in managers:
        outfile = os.path.join(tempfile.gettempdir(), '%s.txt' % _('Pacman - Package list'))
        fh = open(outfile, 'w')
        retval, stdout, stderr = fwbackups.execute('pacman -Qq', env=self.environment, shell=True, stdoutfd=open(outfile, 'w'))
        fh.write(stdout.read())
        fh.close()
        managers.append('pacman')
      if os.path.exists(os.path.join(path, 'dpkg')) and not 'dpkg' in managers:
        outfile = os.path.join(tempfile.gettempdir(), '%s.txt' % _('dpkg - Package list'))
        retval, stdout, stderr = fwbackups.execute('dpkg -l', env=self.environment, shell=True, stdoutfd=open(outfile, 'w'))
        stdout.close()
        managers.append('dpkg')
    return managers
  
  def createDiskInfo(self):
    """Print disk info to a file in tempdir"""
    retval, stdout, stderr = fwbackups.execute('fdisk -l', env=self.environment, shell=True)
    outfile = os.path.join(tempfile.gettempdir(), '%s.txt' % _('Disk Information'))
    fh = open(outfile, 'w')
    fh.write(stdout.read())
    fh.close()

  def parseCommand(self, config):
    """Parse options to retrieve the correct command"""
    self.options = self.getOptions(self.config)
    if self.options['DestinationType'] == 'remote (ssh)':
      tempDir = tempfile.gettempdir()
      self.dest = os.path.join(tempDir, os.path.split(self.dest.replace("'", "'\\''"))[1])
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
      command = 'tar rf \'%s\'' % (self.dest.replace("'", "'\\''"))
    elif self.options['Engine'] == 'tar.gz':
      # DON'T rfz - Can't use r (append) and z (gzip) together
      command = 'tar cfz \'%s\'' % (self.dest.replace("'", "'\\''"))
    elif self.options['Engine'] == 'tar.bz2':
      # DON'T rfz - Can't use r (append) and z (gzip) together
      command = 'tar cfj \'%s\'' % (self.dest.replace("'", "'\\''"))
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
    
    return command

  def addListFilesToBackup(self, manager, command, engine, pkglist, diskinfo, paths):
    """Adds the pkglist and diskinfo to the backup"""
    self.ifCancel()
    prefix = os.path.join(tempfile.gettempdir(), manager)
    if engine == 'tar':
      if pkglist:
        fwbackups.execute("%s '%s - %s.txt' '%s'" % (command, prefix, _('Package list'), self.dest.replace("'", "'\\''")),
          env=self.environment, shell=True, timeout=-1)
      if diskinfo:
        fwbackups.execute("%s '%s - %s.txt' '%s'" % (command, prefix, _('Disk Information'), self.dest.replace("'", "'\\''")),
          env=self.environment, shell=True, timeout=-1)
    elif engine in ['tar.gz', 'tar.bz2']:
      if pkglist:
        paths.append('"%s - %s.txt"' % (prefix, _('Package list')))
      if diskinfo:
        paths.append('"%s.txt"' % os.path.join(tempfile.gettempdir(), _('Disk Information')))
    elif engine == 'rsync':
      if pkglist:
        fwbackups.execute("%s '%s - %s.txt' '%s'" % (command, prefix, _('Package list'), self.dest.replace("'", "'\\''")), env=self.environment, shell=True, timeout=-1)
      if diskinfo:
        # .replace("'", "'\\''") = wrap it in quotes for command line, and escape other single quote)
        diskInfoFile = os.path.join(tempfile.gettempdir(), _('Disk Information'))
        fwbackups.execute("%s '%s.txt' '%s'" % (command, diskInfoFile, self.dest.replace("'", "'\\''")), env=self.environment, shell=True, timeout=-1)

  def deleteListFiles(self, manager, pkglist, diskinfo):
    """Delete the list files in the tempdir"""
    prefix = os.path.join(tempfile.gettempdir(), manager)
    if self.options['PkgListsToFile']:
      os.remove('%s - %s.txt' % (prefix, _('Package list')) )
    if self.options['DiskInfoToFile']:
      os.remove('%s.txt' % os.path.join(tempfile.gettempdir(), _('Disk Information')))
    self.ifCancel()
  
  def checkRemoteServer(self):
    """Checks if a connection to the remote server can be established"""
    if self.options['DestinationType'] == 'remote (ssh)': # check if server settings are OK
      self.logger.logmsg('DEBUG', _('Attempting to connect to server'))
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
        import tarfile
        fh = tarfile.open(self.dest, 'w')
        for i in paths:
          self.ifCancel()
          self._current += 1
          # let's deal with real paths
          i = i[1:-1]
          self.logger.logmsg('INFO', _('Using %s on Windows: Cancel function will only take effect after a path has been completed.' % self.options['Engine']))
          self.logger.logmsg('DEBUG', _('Backing up path %(a)i/%(b)i: %(c)s' % {'a': self._current, 'b': self._total, 'c': i}))
          fh.add(i, recursive=self.options['Recursive'])
        fh.close()
      else:
        for i in paths:
          self.ifCancel()
          self._current += 1
          self.logger.logmsg('DEBUG', _('Running command: nice -n %(a)i %(b)s %(c)s' % {'a': self.options['Nice'], 'b': command, 'c': i}))
          sub = fwbackups.executeSub('nice -n %i %s %s' % (self.options['Nice'], command, i), env=self.environment, shell=True)
          self.pids.append(sub.pid)
          self.logger.logmsg('DEBUG', _('Starting subprocess with PID %s') % sub.pid)
          # Sleep while not done.
          while sub.poll() in ["", None]:
            time.sleep(0.01)
          self.pids.remove(sub.pid)
          retval = sub.poll()
          self.logger.logmsg('DEBUG', _('Subprocess with PID %(a)s exited with status %(b)s' % {'a': sub.pid, 'b': retval}))
          # Something wrong?
          if retval != EXIT_STATUS_OK and retval != 2:
            wasAnError = True
            self.logger.logmsg('ERROR', 'Error(s) occurred while backing up path \'%s\'.\nPlease check the error output below to determine if any files are incomplete or missing.' % str(i))
            self.logger.logmsg('ERROR', _('Output:\n%s') % ('Return value: %s\nstdout: %s\nstderr: %s' % (retval, ''.join(sub.stdout.readlines()), ''.join(sub.stderr.readlines()) )))
      
    elif self.options['Engine'] == 'tar.gz':
      self._total = 1
      self._current = 1
      if MSWINDOWS:
        import tarfile
        fh = tarfile.open(self.dest, 'w:gz')
        for i in paths:
          self.ifCancel()
          # let's deal with real paths
          i = i[1:-1]
          self.logger.logmsg('INFO', _('Using %s on Windows: Cancel function will only take effect after a path has been completed.' % self.options['Engine']))
          self.logger.logmsg('DEBUG', _('Backing up path %(a)i/%(b)i: %(c)s' % {'a': self._current, 'b': self._total, 'c': i}))
          fh.add(i, recursive=self.options['Recursive'])
          self.logger.logmsg('DEBUG', _('Adding path `%s\' to the archive' % i))
        fh.close()
      else:
        i = ' '.join(paths)
        self.logger.logmsg('INFO', _('Using %s: Must backup all paths at once - Progress notification will be disabled.' % self.options['Engine']))
        self.logger.logmsg('DEBUG', _('Backing up path %(a)i/%(b)i: %(c)s') % {'a': self._current, 'b': self._total, 'c': i.replace("'", '')})
        self.logger.logmsg('DEBUG', _('Running command: nice -n %(a)i %(b)s %(c)s' % {'a': self.options['Nice'], 'b': command, 'c': i}))
        sub = fwbackups.executeSub('nice -n %i %s %s' % (self.options['Nice'], command, i), env=self.environment, shell=True)
        self.pids.append(sub.pid)
        self.logger.logmsg('DEBUG', _('Starting subprocess with PID %s') % sub.pid)
        # Sleep while not done.
        while sub.poll() in ["", None]:
          time.sleep(0.01)
        self.pids.remove(sub.pid)
        retval = sub.poll()
        self.logger.logmsg('DEBUG', _('Subprocess with PID %(a)s exited with status %(b)s' % {'a': sub.pid, 'b': retval}))
        # Something wrong?
        if retval != EXIT_STATUS_OK and retval != 2:
          wasAnError = True
          self.logger.logmsg('ERROR', 'Error(s) occurred while backing up path \'%s\'.\nPlease check the error output below to determine if any files are incomplete or missing.' % str(i))
          self.logger.logmsg('ERROR', _('Output:\n%s') % ('Return value: %s\nstdout: %s\nstderr: %s' % (retval, ''.join(sub.stdout.readlines()), ''.join(sub.stderr.readlines()) )))
          
    elif self.options['Engine'] == 'tar.bz2':
      self._total = 1
      self._current += 1
      if MSWINDOWS:
        import tarfile
        fh = tarfile.open(self.dest, 'w:bz2')
        for i in paths:
          self.ifCancel()
          # let's deal with real paths
          i = i[1:-1]
          self.logger.logmsg('INFO', _('Using %s on Windows: Cancel function will only take effect after a path has been completed.' % self.options['Engine']))
          self.logger.logmsg('DEBUG', _('Backing up path %(a)i/%(b)i: %(c)s' % {'a': self._current, 'b': self._total, 'c': i}))
          fh.add(i, recursive=self.options['Recursive'])
          self.logger.logmsg('DEBUG', _('Adding path `%s\' to the archive' % i))
        fh.close()
      else:
        i = ' '.join(paths)
        self.logger.logmsg('INFO', _('Using %s: Must backup all paths at once - Progress notification will be disabled.' % self.options['Engine']))
        self.logger.logmsg('DEBUG', _('Backing up path %(a)i/%(b)i: %(c)s') % {'a': self._current, 'b': self._total, 'c': i})
        self.logger.logmsg('DEBUG', _('Running command: nice -n %(a)i %(b)s %(c)s' % {'a': self.options['Nice'], 'b': command, 'c': i}))
        sub = fwbackups.executeSub('nice -n %i %s %s' % (self.options['Nice'], command, i), env=self.environment, shell=True)
        self.pids.append(sub.pid)
        self.logger.logmsg('DEBUG', _('Starting subprocess with PID %s') % sub.pid)
        # Sleep while not done.
        while sub.poll() in ["", None]:
          time.sleep(0.01)
        self.pids.remove(sub.pid)
        retval = sub.poll()
        self.logger.logmsg('DEBUG', _('Subprocess with PID %(a)s exited with status %(b)s' % {'a': sub.pid, 'b': retval}))
        # Something wrong?
        if retval != EXIT_STATUS_OK and retval != 2:
          wasAnError = True
          self.logger.logmsg('ERROR', 'Error(s) occurred while backing up path \'%s\'.\nPlease check the error output below to determine if any files are incomplete or missing.' % str(i))
          self.logger.logmsg('ERROR', _('Output:\n%s') % ('Return value: %s\nstdout: %s\nstderr: %s' % (retval, ''.join(sub.stdout.readlines()), ''.join(sub.stderr.readlines()) )))
    
    elif self.options['Engine'] == 'rsync':
      # in this case, self.{folderdest,dest} both need to be created
      if self.options['DestinationType'] == 'remote (ssh)':
        client, sftpClient = sftp.connect(self.options['RemoteHost'], self.options['RemoteUsername'], self.options['RemotePassword'], self.options['RemotePort'])
        if not wasAnError:
          for i in paths:
            i = i[1:-1]
            sftp.put(sftpClient, i, os.path.normpath(self.options['RemoteFolder']+os.sep+os.path.basename(self.dest)+os.sep+os.path.dirname(i)), symlinks=not self.options['FollowLinks'], excludes=self.options['Excludes'].split('\n'))
        sftpClient.close()
        client.close()
      else:
        for i in paths:
          self.ifCancel()
          self._current += 1
          if MSWINDOWS:
            # let's deal with real paths
            i = i[1:-1]
            self.logger.logmsg('DEBUG', _('Backing up path %(a)i/%(b)i: %(c)s' % {'a': self._current, 'b': self._total, 'c': i}))
            shutil_modded.copytree_fullpaths(i, self.dest)
            self._current += 1
          else:
            self.logger.logmsg('DEBUG', _("Running command: nice -n %(a)i %(b)s %(c)s '%(d)s'" % {'a': self.options['Nice'], 'b': command, 'c': i, 'd': self.dest.replace("'", "'\\''")}))
            sub = fwbackups.executeSub("nice -n %i %s %s '%s'" % (self.options['Nice'], command, i, self.dest.replace("'", "'\\''")), env=self.environment, shell=True)
            self.pids.append(sub.pid)
            self.logger.logmsg('DEBUG', _('Starting subprocess with PID %s') % sub.pid)
            # Sleep while not done.
            while sub.poll() in ["", None]:
              time.sleep(0.01)
            self.pids.remove(sub.pid)
            retval = sub.poll()
            self.logger.logmsg('DEBUG', _('Subprocess with PID %(a)s exited with status %(b)s' % {'a': sub.pid, 'b': retval}))
            # Something wrong?
            if retval != EXIT_STATUS_OK and retval != 2:
              wasAnError = True
              self.logger.logmsg('ERROR', "Error(s) occurred while backing up path '%s'.\nPlease check the error output below to determine if any files are incomplete or missing." % str(i))
              self.logger.logmsg('ERROR', _('Output:\n%s') % ('Return value: %s\nstdout: %s\nstderr: %s' % (retval, ''.join(sub.stdout.readlines()), ''.join(sub.stderr.readlines()) )))
    
    if self.options['Engine'].startswith('tar') and self.options['DestinationType'] == 'remote (ssh)':
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
  def __init__(self, logger=None):
    """Initializes a one-time backup operation. If no logger is specified, a new one
    will be created. logger will be created if needed."""
    BackupOperation.__init__(self, logger)
    self.logger.logmsg('INFO', _('Starting one-time backup operation'))
    self.config = config.OneTimeConf(ONETIMELOC)
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
      return False
    
    self.checkRemoteServer()
    
    if self.options['PkgListsToFile']:
      managers = self.createPkgLists()
    else:
      managers = []
    if self.options['DiskInfoToFile']:
      self.createDiskInfo()

    if not (self.options['Engine'] == 'rsync' and self.options['Incremental'] and \
       not self.options['DestinationType'] == 'remote (ssh)'):
      if not self.prepareDestinationFolder(self.options['Destination']):
        return False
      if os.path.exists(self.dest):
        self.logger.logmsg('WARNING', _('`%s\' exists and will be overwritten.') % self.dest)
        shutil_modded.rmtree(path=self.dest, onerror=self.onError)
    self.ifCancel()

    command = self.parseCommand(self.config)
    for manager in managers:
      self.addListFilesToBackup(manager, command, self.options['Engine'], self.options['PkgListsToFile'], self.options['DiskInfoToFile'], paths)

    # Now that the paths & commands are set up...
    errorBool = self.backupPaths(paths, command)

    for manager in managers:
      self.deleteListFiles(manager, self.options['PkgListsToFile'], self.options['DiskInfoToFile'])
    self.ifCancel()

    if self.options['DestinationType'] == 'local':
      try:
        os.chmod(self.dest, 0711)
      except:
        pass

    # All done!
    self.logger.logmsg('INFO', _('Finished one-time backup'))
    return errorBool

######################
######################
class SetBackupOperation(BackupOperation):
  """Automated set backup operation"""
  def __init__(self, setName, logger=None):
    """Initializes the automatic backup operation of setname. If no logger is
    supplied, a new one will be created."""
    BackupOperation.__init__(self, logger)
    self.config = config.BackupSetConf(os.path.join(SETLOC, "%s.conf" % setName))
    self.options = self.getOptions(self.config)
    if self.options['Enabled']:
      self.logger.logmsg('INFO', _('Starting automatic backup operation of set `%s\'') % self.config.getSetName())
    # Parse backup folder format
    date = time.strftime('%Y-%m-%d_%H-%M')
    self.dest = os.path.join(self.options['Destination'], "%s-%s-%s" % (_('Backup'), self.config.getSetName(), date))
    # set-specific options
    self.command_before = self.options['CommandBefore']
    self.command_after = self.options['CommandAfter']
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
  
  def removeOldBackups(self):
    """Get list of old backups and remove them"""
    # get listing, local or remote
    if self.options['DestinationType'] == 'remote (ssh)':
      client, sftpClient = sftp.connect(self.options['RemoteHost'], self.options['RemoteUsername'], self.options['RemotePassword'], self.options['RemotePort'])
      listing = sftpClient.listdir(self.options['RemoteFolder'])
    else:
      listing = os.listdir(self.options['Destination'])
    listing.sort()
    oldbackups = []
    for i in listing:
      if i.startswith('%s-%s-' % (_('Backup'), self.config.getSetName())):
        oldbackups.append(i)
    # ...And remove them.
    oldbackups.reverse()
    if self.options['DestinationType'] == 'remote (ssh)':
      for i in oldbackups[self.options['OldToKeep']:]:
        sftp.remove(sftpClient, os.path.join(self.options['RemoteFolder'], i))
      sftpClient.close()
      client.close()
    else:
      if self.options['Engine'] == 'rsync' and self.options['Incremental'] and oldbackups:
        for i in oldbackups[:-1]:
          self.logger.logmsg('DEBUG', _('Removing old backup `%s\'') % i)
          shutil_modded.rmtree(path=os.path.join(self.options['Destination'], i), onerror=self.onError)
        oldIncrementalBackup = os.path.join(self.options['Destination'], oldbackups[-1])
        if not oldIncrementalBackup.endswith('.tar') and not oldIncrementalBackup.endswith('.tar.gz') and \
            not oldIncrementalBackup.endswith('.tar.bz2'): # oldIncrementalBackup = rsync
          self.logger.logmsg('DEBUG', _('Moving  `%s\' to `%s\'') % (oldIncrementalBackup, self.dest))
          shutil_modded.move(oldIncrementalBackup, self.dest)
        else: # source = is not a rsync backup - remove it and start fresh
          self.logger.logmsg('DEBUG', _('`%s\' is not an rsync backup - removing.') % oldIncrementalBackup)
          shutil_modded.rmtree(path=oldIncrementalBackup, onerror=self.onError)
      else:
        for i in oldbackups[self.options['OldToKeep']:]:
          self.logger.logmsg('DEBUG', _('Removing old backup `%s\'') % i)
          shutil_modded.rmtree(path=os.path.join(self.options['Destination'], i), onerror=self.onError)

  def start(self):
    """Backup a set"""
    if self.options['Enabled'] == '0': # set is disabled
      return True
    # Get the list of paths...
    paths = self.parsePaths(self.config)
    if not paths:
      return False
    
    self.checkRemoteServer()
    
    self._status = STATUS_CLEANING_OLD
    if not (self.options['Engine'] == 'rsync' and self.options['Incremental']) and \
       not self.options['DestinationType'] == 'remote (ssh)':
      if not self.prepareDestinationFolder(self.options['Destination']):
        return False
      if not (self.options['Engine'] == 'rsync' and self.options['Incremental']) \
      and os.path.exists(self.dest):
        self.logger.logmsg('WARNING', _('`%s\' exists and will be overwritten.') % self.dest)
        shutil_modded.rmtree(path=self.dest, onerror=self.onError)
    self.ifCancel()
    
    # Remove old stuff
    self.removeOldBackups()
    self.ifCancel()
    
    # Before command...
    if self.command_before:
      self._status = STATUS_EXECING_USER_COMMAND
      self.logger.logmsg('INFO', _("Executing 'Before' command"))
      sub = fwbackups.executeSub(self.command_before, env=self.environment, shell=True)
      self.pids.append(sub.pid)
      self.logger.logmsg('DEBUG', _('Starting subprocess with PID %s') % sub.pid)
      # Sleep while not done.
      while sub.poll() in ["", None]:
        time.sleep(0.01)
      self.pids.remove(sub.pid)
      retval = sub.poll()
      # Something wrong?
      if retval != EXIT_STATUS_OK:
        self.logger.logmsg('ERROR', _('Command returned with a non-zero exit status:'))
        self.logger.logmsg('ERROR', 'Return value: %s\nstdout: %s\nstderr: %s' % (retval, ''.join(sub.stdout.readlines()), ''.join(sub.stderr.readlines()) ))
      self.ifCancel()
    
    self._status = STATUS_INITIALIZING
    if self.options['PkgListsToFile']:
      managers = self.createPkgLists()
    else:
      managers = []
    if self.options['DiskInfoToFile']:
      self.createDiskInfo()
    self.ifCancel()
    command = self.parseCommand(self.config)
    for manager in managers:
      self.addListFilesToBackup(manager, command, self.options['Engine'], self.options['PkgListsToFile'], self.options['DiskInfoToFile'], paths)
    # Now that the paths & commands are set up...
    errorBool = self.backupPaths(paths, command)
    for manager in managers:
      self.deleteListFiles(manager, self.options['PkgListsToFile'], self.options['DiskInfoToFile'])
    if self.options['DestinationType'] == 'local':
      try:
        os.chmod(self.dest, 0711)
      except:
        pass
    
    # After command
    if self.command_after:
      self._status = 4
      self.logger.logmsg('INFO', _("Executing 'After' command"))
      sub = fwbackups.executeSub(self.command_after, env=self.environment, shell=True)
      self.pids.append(sub.pid)
      self.logger.logmsg('DEBUG', _('Starting subprocess with PID %s') % sub.pid)
      # Sleep while not done.
      while sub.poll() in ["", None]:
        time.sleep(0.01)
      self.pids.remove(sub.pid)
      retval = sub.poll()
      # Something wrong?
      if retval != EXIT_STATUS_OK:
        self.logger.logmsg('ERROR', _('Command returned with a non-zero exit status:'))
        self.logger.logmsg('ERROR', 'Return value: %s\nstdout: %s\nstderr: %s' % (retval, ''.join(sub.stdout.readlines()), ''.join(sub.stderr.readlines()) ))

    # All done!
    self.logger.logmsg('INFO', _("Finished automatic backup operation of set '%s'") % self.config.getSetName())
    return errorBool
