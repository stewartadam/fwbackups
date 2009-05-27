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
This file contains the logic for the restore operation
"""
import os
import tarfile
import time
#--
import fwbackups
from fwbackups.const import *
from fwbackups.i18n import _
from fwbackups import config
from fwbackups import operations
from fwbackups import shutil_modded
from fwbackups import sftp

STATUS_INITIALIZING = 0
STATUS_RESTORING = 1
STATUS_RECEIVING_FROM_REMOTE = 2

class RestoreOperation(operations.Common):
  def __init__(self, logger=None):
    """Initializes a restore operation. If no logger is specified, a new one
    will be created."""
    operations.Common.__init__(self, logger)
    self.logger.logmsg('INFO', _('Starting restore operation'))
    self.config = config.RestoreConf()
    self.options = self.getOptions(self.config)
    self.options['Engine'] = 'null' # workaround so prepareDestinationFolder doesn't complain

  def getOptions(self, conf):
    """Loads all the configuration options from a restore configuration file and
    returns them in a dictionary"""
    def _bool(value):
      return value in [1, '1', True, 'True']
    options = {}
    for option in conf.options('Options'):
      options[option] = conf.get('Options', option)
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
    if self.options['SourceType'] == 'remote archive (SSH)': # check if server settings are OK
      self.logger.logmsg('DEBUG', _('Attempting to connect to server'))
      thread = fwbackups.runFuncAsThread(sftp.testConnection, True,
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
      elif thread.retval == False:
        self.logger.logmsg('ERROR', _('The selected file or folder was either not ' + \
                       'found or the user specified cannot write to it.'))
        return False
      elif thread.retval[0] == paramiko.AuthenticationException:
        self.logger.logmsg('ERROR', _('A connection was established, but authentication ' + \
                        'failed. Please verify the username and password ' + \
                        'and try again.'))
        return False
      elif thread.retval[0] == socket.gaierror or thread.retval[0] == socket.error:
        self.logger.logmsg('ERROR', _('A connection to the server could not be established.\n' + \
                        'Error %(a)s: %(b)s' % {'a': thread.retval[1][0], 'b': thread.retval[1][1]} + \
                        '\nPlease verify your settings and try again.'))
        return False
      elif thread.retval[0] == socket.timeout:
        self.logger.logmsg('ERROR', _('A connection to the server has timed out. ' + \
                        'Please verify your settings and try again.'))
        return False
      elif thread.retval[0] == paramiko.SSHException:
        self.logger.logmsg('ERROR', _('A connection to the server could not be established ' + \
                        'because an error occurred: %s' % thread.retval[1] + \
                        '\nPlease verify your settings and try again.'))
        return False
    # source types:     'set' 'local archive' 'local folder'
    #                   'remote archive (SSH)'

    # We don't want to raise a hard error, that's already in the log.
    # So we settle for a simple return false.
    # don't need source type logic, /destination/ is always a folder
    if not self.prepareDestinationFolder(self.options['Destination']):
      return False
    if self.options['SourceType'] == 'remote archive (SSH)' or (self.options['SourceType'] == 'set' and self.options['RemoteSource']):
      self.logger.logmsg('INFO', _('Receiving files from server'))
      self._status = 2 # receiving files
      try:
        # download file to location where we expect source to be
        client, sftpClient = sftp.connect(self.options['RemoteHost'], self.options['RemoteUsername'], self.options['RemotePassword'], self.options['RemotePort'])
        retval = sftp.getFile(sftpClient, self.options['RemoteSource'], self.options['Source'])
        sftpClient.close()
        client.close()
        if retval == -1: # folder - not implemented yet
          self.logger.logmsg('ERROR', _('Restoring from a remote folder is not supported yet.'))
          return False
      except Exception, error:
        self.logger.logmsg('DEBUG', _('Could not receive file from server: %s' % error))
        wasErrors = True
    self.status = 1 # restoring
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
