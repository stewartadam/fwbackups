#! /usr/bin/python
# -*- coding: utf-8 -*-
#  Copyright (C) 2009 Stewart Adam
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
import os
import random
import sys

sys.path.append(os.path.join(os.getcwd(), 'src'))
from fwbackups.i18n import _
from fwbackups.const import USER, USERHOME
from fwbackups import config
from fwbackups.operations import backup, restore, OperationError
from fwbackups import sftp
from fwbackups import shutil_modded

TESTDIR = os.path.join(os.getcwd(), 'tests')
SOURCEDIR = os.path.join(TESTDIR, 'sourcefiles')
DESTDIR_BACKUP = os.path.join(TESTDIR, 'destination')
DESTDIR_RESTORE = os.path.join(TESTDIR, 'restores')

paths = [SOURCEDIR]

print _("*** Initializing files")
for directory in [TESTDIR, SOURCEDIR, DESTDIR_BACKUP, DESTDIR_RESTORE]:
  if os.path.exists(directory):
    print _("Folder %s exists and will be emptied. Press <Enter> to confirm or <ctrl+c> to cancel...") % directory
    try:
      raw_input()
    except KeyboardInterrupt:
      print
      sys.exit(0)
    print _("Cleaning folder %s...") % directory
    shutil_modded.rmtree(directory)
  os.mkdir(directory)

# Initialize 50MB of files
for num in range(0, 50):
  fh = open(os.path.join(SOURCEDIR, "file%s" % num), 'w')
  fh.write(random.choice('abcdefghijklmnopqrstuvwxyz1234567890-=+_;"}{[]|<>/?.,`~')*1048576)
  fh.close()

print _("*** Remote settings")
hostname = raw_input(_("Hostname [localhost]: ")) or 'localhost'
while True:
  port = raw_input(_("Port [22]: ")) or '22'
  try:
    int(port)
    break
  except:
    print _("The port field can only contain numbers. Please try again.")
username = raw_input(_("Username [%s]: ") % USER) or USER
password = raw_input(_("Password: ")).encode("base64")
remotefolder = raw_input(_("Remote folder [%s]: ") % USERHOME) or USERHOME

options = {}
options["BackupHidden"] = 1
options["CommandAfter"] = ""
options["CommandBefore"] = ""
options["Destination"] = DESTDIR_BACKUP
options["DiskInfoToFile"] = 0
options["Enabled"] = 0
options["Excludes"] = ""
options["FollowLinks"] = 0
options["Incremental"] = 0
options["Nice"] = 0
options["OldToKeep"] = 99
options["PkgListsToFile"] = 1
options["Recursive"] = 1
options["RemoteFolder"] = remotefolder
options["RemoteHost"] = hostname
options["RemotePassword"] = password
options["RemotePort"] = port
options["RemoteUsername"] = username
options["Sparse"] = "0"
times = {}
times["Custom"] = "False"
times["Entry"] = "0 0 * 1 0"

for destType in ["remote (ssh)", "local"]:
  for engine in ["rsync", "tar", "tar.gz", "tar.bz2"]:
    print _("*** Running %(a)s backup with engine %(b)s" % {'a': destType, 'b': engine})
    options["DestinationType"] = destType
    options["Engine"] = engine
    SETPATH = os.path.join(TESTDIR, "backup-%s-%s.conf" % (destType, engine))
    if os.path.exists(SETPATH):
      os.remove(SETPATH)
    setConf = config.BackupSetConf(SETPATH, create=True)
    setConf.save(paths, options, times)
    operation = backup.SetBackupOperation(SETPATH)
    operation.logger.setPrintToo(True)
    if not operation.start() == True:
      raise OperationError(_("Backup failed!"))
    print '\n'

#
# Restore
#

# Remote set backups
options = {}
options["RemoteHost"] = hostname
options["RemotePassword"] = password
options["RemotePort"] = 22
options["RemoteUsername"] = username
options["SourceType"] = "set"

for engine in ["rsync", "tar", "tar.gz", "tar.bz2"]:
  setName = "backup-remote (ssh)-%s" % engine
  print _("*** Running restore of remote test backup %s" % setName)
  RESTOREPATH = os.path.join(TESTDIR, "restore-remote (ssh)-%s.conf" % engine)
  SETPATH = os.path.join(TESTDIR, "%s.conf" % setName)
  setConfig = config.BackupSetConf(SETPATH)
  restoreConfig = config.RestoreConf(RESTOREPATH, create=True)
  remoteFolder = setConfig.get("Options", "RemoteFolder")
  client, sftpClient = sftp.connect(hostname, username, password.decode('base64'), port)
  listing = sftpClient.listdir(remoteFolder)
  sftpClient.close()
  client.close()
  for backupName in listing:
    if backupName.startswith("%s-%s" % (_("Backup"), setName)):
      options["RemoteSource"] = os.path.join(remoteFolder, backupName)
      # Restore into a subdir with backup name
      restoreDestination = os.path.join(DESTDIR_RESTORE, setName)
      os.mkdir(restoreDestination)
      options["Destination"] = restoreDestination
      options["Source"] = os.path.join(restoreDestination, backupName)
      break
  restoreConfig.save(options)
  operation = restore.RestoreOperation(RESTOREPATH)
  operation.logger.setPrintToo(True)
  if not operation.start() == True:
    raise OperationError(_("Restore failed!"))
  print '\n'

# Local set backups
options = {}
options["RemoteHost"] = ''
options["RemotePassword"] = ''
options["RemotePort"] = 22
options["RemoteUsername"] = ''
options["RemoteSource"] = ''
options["SourceType"] = "set"
for engine in ["rsync", "tar", "tar.gz", "tar.bz2"]:
  setName = "backup-local-%s" % engine
  print _("*** Running restore of local test backup %s" % setName)
  RESTOREPATH = os.path.join(TESTDIR, "restore-local-%s.conf" % engine)
  restoreConfig = config.RestoreConf(RESTOREPATH, create=True)
  listing = os.listdir(DESTDIR_BACKUP)
  for backupName in listing:
    if backupName.startswith("%s-%s" % (_("Backup"), setName)):
      # Restore into a subdir with backup name
      restoreDestination = os.path.join(DESTDIR_RESTORE, setName)
      os.mkdir(restoreDestination)
      options["Destination"] = restoreDestination
      options["Source"] = os.path.join(DESTDIR_BACKUP, backupName)
      break
  restoreConfig.save(options)
  operation = restore.RestoreOperation(RESTOREPATH)
  operation.logger.setPrintToo(True)
  if not operation.start() == True:
    raise OperationError(_("Restore failed!"))
  print '\n'

# Local archive
print _("*** Running restore of a local archive")
name = "restore-local-archive"
restoreDestination = os.path.join(DESTDIR_RESTORE, name)
options = {}
options["Destination"] = restoreDestination
options["RemoteHost"] = ''
options["RemotePassword"] = ''
options["RemotePort"] = 22
options["RemoteUsername"] = ''
options["RemoteSource"] = ''
for item in os.listdir(DESTDIR_BACKUP):
  if item.endswith('.tar'):
    options["Source"] = os.path.join(DESTDIR_BACKUP, item)
    options["SourceType"] = "local archive"
    break
RESTOREPATH = os.path.join(TESTDIR, "%s.conf" % name)
restoreConfig = config.RestoreConf(RESTOREPATH, create=True)
restoreConfig.save(options)
operation = restore.RestoreOperation(RESTOREPATH)
operation.logger.setPrintToo(True)
if not operation.start() == True:
  raise OperationError(_("Restore failed!"))
print '\n'

# Local folder
print _("*** Running restore of a local folder")
name = "restore-local-folder"
restoreDestination = os.path.join(DESTDIR_RESTORE, name)
options = {}
options["Destination"] = restoreDestination
options["RemoteHost"] = ''
options["RemotePassword"] = ''
options["RemotePort"] = 22
options["RemoteUsername"] = ''
options["RemoteSource"] = ''
for item in os.listdir(DESTDIR_BACKUP):
  if not item.endswith('.tar') and  not item.endswith('.tar.gz') and not item.endswith('.tar.bz2'):
    options["Source"] = os.path.join(DESTDIR_BACKUP, item)
    options["SourceType"] = "local folder"
    break
RESTOREPATH = os.path.join(TESTDIR, "%s.conf" % name)
restoreConfig = config.RestoreConf(RESTOREPATH, create=True)
restoreConfig.save(options)
operation = restore.RestoreOperation(RESTOREPATH)
operation.logger.setPrintToo(True)
if not operation.start() == True:
  raise OperationError(_("Restore failed!"))
print '\n'

# Remote archive (SSH)
print _("*** Running restore of a remote archive (SSH)")
name = "restore-remote-archive (SSH)"
restoreDestination = os.path.join(DESTDIR_RESTORE, name)
options = {}
options["Destination"] = restoreDestination
options["RemoteHost"] = hostname
options["RemotePassword"] = password
options["RemotePort"] = 22
options["RemoteUsername"] = username
client, sftpClient = sftp.connect(hostname, username, password.decode('base64'), port)
try:
  listing = sftpClient.listdir(remotefolder)
finally:
  sftpClient.close()
  client.close()
for item in listing:
  if item.endswith('.tar'):
    options["RemoteSource"] = os.path.join(remotefolder, item)
    options["Source"] = os.path.join(restoreDestination, item)
    options["SourceType"] = "remote archive (SSH)"
    break
RESTOREPATH = os.path.join(TESTDIR, "%s.conf" % name)
restoreConfig = config.RestoreConf(RESTOREPATH, create=True)
restoreConfig.save(options)
operation = restore.RestoreOperation(RESTOREPATH)
operation.logger.setPrintToo(True)
if not operation.start() == True:
  raise OperationError(_("Restore failed!"))
print '\n'

# Remote folder (SSH)
print _("*** Running restore of a remote folder (SSH)")
name = "restore-remote-folder (SSH)"
restoreDestination = os.path.join(DESTDIR_RESTORE, name)
options = {}
options["Destination"] = restoreDestination
options["RemoteHost"] = hostname
options["RemotePassword"] = password
options["RemotePort"] = 22
options["RemoteUsername"] = username
client, sftpClient = sftp.connect(hostname, username, password.decode('base64'), port)
try:
  listing = sftpClient.listdir(remotefolder)
  for item in listing:
    if sftp.isFolder(sftpClient, os.path.join(remotefolder, item)):
      options["RemoteSource"] = os.path.join(remotefolder, item)
      options["Source"] = os.path.join(restoreDestination, item)
      options["SourceType"] = "remote archive (SSH)"
      break
finally:
  sftpClient.close()
  client.close()
RESTOREPATH = os.path.join(TESTDIR, "%s.conf" % name)
restoreConfig = config.RestoreConf(RESTOREPATH, create=True)
restoreConfig.save(options)
operation = restore.RestoreOperation(RESTOREPATH)
operation.logger.setPrintToo(True)
if not operation.start() == True:
  raise OperationError(_("Restore failed!"))
print '\n'
