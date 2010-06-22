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
This file contains the logic for the restore operation
"""
import os
import tarfile
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
STATUS_RESTORING = 1
STATUS_RECEIVING_FROM_REMOTE = 2

class RestoreOperation(operations.Common):
  def __init__(self, restorePath, logger=None):
    """Initializes a restore operation. If no logger is specified, a new one
    will be created."""
    operations.Common.__init__(self, logger)
    self.logger.logmsg('INFO', _('Starting restore operation'))
    self.config = config.RestoreConf(restorePath)
    self.options = self.getOptions(self.config)
    self.options['Engine'] = 'null' # workaround so prepareDestinationFolder doesn't complain

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
    options['RemotePassword'] = options['RemotePassword'].decode('base64')
    return options

  def tarfile_generator(self, members):
    """Generator function for the tar extraction"""
    for tarinfo in members:
      self.ifCancel(members)
      self._currentName = os.path.basename(tarinfo.name)
      yield tarinfo

  def start(self):
    """Restores a backup"""
    wasErrors = False
    if self.options['RemoteSource']: # check if server settings are OK
      self.logger.logmsg('DEBUG', _('Attempting to connect to server'))
      thread = fwbackups.runFuncAsThread(sftp.testConnection,
                                         self.options['RemoteHost'], self.options['RemoteUsername'],
                                         self.options['RemotePassword'], self.options['RemotePort'],
                                         self.options['RemoteSource'])
      while thread.retval == None:
        time.sleep(0.1)
      # Check for errors, if any
      import paramiko
      import socket
      if thread.retval == True:
        pass
      elif type(thread.exception) == IOError:
        self.logger.logmsg('ERROR', _('The restore source was either not ' + \
                       'found or it cannot be read due to insufficient permissions.'))
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
    # source types:     'set' 'local archive' 'local folder'
    #                   'remote archive (SSH)', 'remote folder (SSH)'

    # We don't want to raise a hard error, that's already in the log.
    # So we settle for a simple return false.
    # don't need source type logic, /destination/ is always a folder
    if not self.prepareDestinationFolder(self.options['Destination']):
      return False
    # Receive files from remote server
    if self.options['RemoteSource']:
      self.logger.logmsg('INFO', _('Receiving files from server'))
      self._status = STATUS_RECEIVING_FROM_REMOTE # receiving files
      try:
        # download file to location where we expect source to be
        client, sftpClient = sftp.connect(self.options['RemoteHost'], self.options['RemoteUsername'], self.options['RemotePassword'], self.options['RemotePort'])
        retval = sftp.receive(sftpClient, self.options['RemoteSource'], self.options['Destination'])
        # This is used later to terminate the restore operation early
        remoteSourceIsFolder = sftp.isFolder(sftpClient, self.options['RemoteSource'])
        sftpClient.close()
        client.close()
      except Exception, error:
        self.logger.logmsg('ERROR', _('Could not receive file from server: %s' % error))
        wasErrors = True
      if wasErrors or remoteSourceIsFolder:
          # We are dealing with a remote folder - our job here is done
          # Either that or an error was encountered above
          self.logger.logmsg('INFO', _('Finished restore operation'))
          return not wasErrors
    self._status = STATUS_RESTORING # restoring
    try:
      if self.options['SourceType'] == 'set': # we don't know the type
        if os.path.isfile(self.options['Source']):
          fh = tarfile.open(self.options['Source'], 'r')
          fh.extractall(self.options['Destination'], members=self.tarfile_generator(fh))
          fh.close()
        elif os.path.isdir(self.options['Source']): # we are dealing with rsync
          shutil_modded.copytree(self.options['Source'], self.options['Destination'])
        else: # oops, something is up
          self.logger.logmsg('ERROR', _('Source `%s\' is not a file or folder!' % self.options['Source']))
          return False

      elif self.options['SourceType'] == 'local archive' or self.options['SourceType'] == 'remote archive (SSH)':
        if os.path.isfile(self.options['Source']):
          fh = tarfile.open(self.options['Source'], 'r')
          fh.extractall(self.options['Destination'])
          fh.close()
        else: # oops, something is up
          self.logger.logmsg('ERROR', _('Source `%s\' is not an archive!' % self.options['Source']))
          return False
      else: # folders
        if not os.path.isdir(self.options['Source']):
          self.logger.logmsg('ERROR', _('Source `%s\' is not a folder' % self.options['Source']))
          return False
        if not self.prepareDestinationFolder(self.options['Destination']):
          return False
        shutil_modded.copytree(self.options['Source'], self.options['Destination'])
      
      # Clean up transfered files from remote server
      if self.options['SourceType'] == 'remote archive (SSH)' or (self.options['SourceType'] == 'set' and self.options['RemoteSource']):
        os.remove(self.options['Source'])
      
    except:
      self.logger.logmsg('ERROR', 'Error(s) occurred while restoring certain files or folders.\nPlease check the traceback below to determine if any files are incomplete or missing.')
      import sys
      import traceback
      (etype, value, tb) = sys.exc_info()
      tracebackText = ''.join(traceback.format_exception(etype, value, tb))
      self.logger.logmsg('ERROR', _('Traceback: %s' % tracebackText))
      wasErrors = True

    # All done!
    self.logger.logmsg('INFO', _('Finished restore operation'))
    return not wasErrors
