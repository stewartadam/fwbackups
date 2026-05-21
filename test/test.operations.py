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
import base64
import os
import random
import sys

from getpass import getpass

# flake8: noqa E402
sys.path.append(os.path.join(os.getcwd(), '..'))

from fwbackups.i18n import _
from fwbackups.const import USER
from fwbackups import config
from fwbackups.operations import backup, restore, OperationError
from fwbackups import sftp
from fwbackups import shutil_modded

TESTDIR = os.path.join(os.getcwd(), 'tests')
SOURCEDIR = os.path.join(TESTDIR, 'sourcefiles')
DESTDIR_BACKUP = os.path.join(TESTDIR, 'destination')
DESTDIR_RESTORE = os.path.join(TESTDIR, 'restores')

paths = [SOURCEDIR]


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in ('1', 'true', 'yes', 'on')


def prompt_or_env(env_name, prompt, default=None):
    value = os.environ.get(env_name)
    if value is not None:
        return value
    return input(prompt) or default


print(_("*** Initializing files"))
noninteractive = env_bool('FWBACKUPS_TEST_NONINTERACTIVE')
clean_existing = env_bool('FWBACKUPS_TEST_CLEAN', default=noninteractive)
for directory in [TESTDIR, SOURCEDIR, DESTDIR_BACKUP, DESTDIR_RESTORE]:
  if os.path.exists(directory):
    if not clean_existing:
      print(_("Folder %s exists and will be emptied. Press <Enter> to confirm or <ctrl+c> to cancel...") % directory)
      try:
        input()
      except KeyboardInterrupt:
        print()
        sys.exit(0)
    print(_("Cleaning folder %s...") % directory)
    shutil_modded.rmtree(directory)
  os.mkdir(directory)

# Initialize a collection of 1MB of files
MEGABYTE_BYTES = int(os.environ.get('FWBACKUPS_TEST_FILE_SIZE_BYTES', 1048576))
FILE_COUNT = int(os.environ.get('FWBACKUPS_TEST_FILE_COUNT', 50))

def write_file(filename, length_bytes):
    fh = open(filename, 'w')
    fh.write(random.choice('abcdefghijklmnopqrstuvwxyz1234567890-=+_;"}{[]|<>/?.,`~')*length_bytes)
    fh.close()

# Particular filenames to test encodings
utf8_filenames = [
    'file-emoji-🤷‍♂️',
    'file-diacritics-éàîçüø',
    'file-math-÷± a⋅b n→∞ ∑x ¬(α∨β),',
    'file-science-H₂O',
    'file-symbols-© Ω “” ‚ ¿?',
    'file-pronounciation-ˈɪŋɡlənd',
    'file-currencies-$€£¥₹',
    'file-korean-프로그램',
    'file-greek-مرحبا بالعالم',
    'file-chinese-simplified-你好世界',
    'file-russian-Здравствуй, мир!'
]

for filename in utf8_filenames:
    write_file(os.path.join(SOURCEDIR, filename), MEGABYTE_BYTES)

for num in range(0, FILE_COUNT-len(utf8_filenames)):
  write_file(os.path.join(SOURCEDIR, f"file{num}"), MEGABYTE_BYTES)

print(_("*** Remote settings"))
hostname = prompt_or_env('FWBACKUPS_TEST_SSH_HOST', _("Hostname [localhost]: "), 'localhost')
port = os.environ.get('FWBACKUPS_TEST_SSH_PORT')
while port is None:
  port = input(_("Port [22]: ")) or '22'
  try:
    int(port)
    break
  except ValueError:
    print(_("The port field can only contain numbers. Please try again."))
    port = None
try:
  int(port)
except ValueError:
  print(_("The port field can only contain numbers. Please try again."))
  sys.exit(1)
username = prompt_or_env('FWBACKUPS_TEST_SSH_USER', _("Username [%s]: ") % USER, USER)
raw_password = os.environ.get('FWBACKUPS_TEST_SSH_PASSWORD')
if raw_password is None:
  raw_password = getpass(prompt=_("Password: "))
password = base64.b64encode(raw_password.encode('ascii')).decode('ascii')
remotefolder = prompt_or_env('FWBACKUPS_TEST_REMOTE_FOLDER', _("Remote folder [%s]: ") % DESTDIR_RESTORE, DESTDIR_RESTORE)

options = {}
options["BackupHidden"] = 1
options["CommandAfter"] = ""
options["CommandBefore"] = ""
options["Destination"] = DESTDIR_BACKUP
options["DiskInfoToFile"] = 0
options["Enabled"] = 1
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
options["SingleFilesystem"] = 0
times = {}
times["Custom"] = "False"
times["Entry"] = "0 0 * 1 0"

for destType in ["remote (ssh)", "local"]:
  for engine in ["rsync", "tar", "tar.gz", "tar.bz2"]:
    print(_("*** Running %(a)s backup with engine %(b)s" % {'a': destType, 'b': engine}))
    options["DestinationType"] = destType
    options["Engine"] = engine
    SETPATH = os.path.join(TESTDIR, "backup-%s-%s.conf" % (destType, engine))
    if os.path.exists(SETPATH):
      os.remove(SETPATH)
    setConf = config.BackupSetConf(SETPATH, create=True)
    setConf.save(paths, options, times)
    operation = backup.SetBackupOperation(SETPATH)
    operation.logger.setPrintToo(True)
    if not operation.start():
      raise OperationError(_("Backup failed!"))
    print('\n')

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
  print(_("*** Running restore of remote test backup %s" % setName))
  RESTOREPATH = os.path.join(TESTDIR, "restore-remote (ssh)-%s.conf" % engine)
  SETPATH = os.path.join(TESTDIR, "%s.conf" % setName)
  setConfig = config.BackupSetConf(SETPATH)
  restoreConfig = config.RestoreConf(RESTOREPATH, create=True)
  remoteFolder = setConfig.get("Options", "RemoteFolder")
  client, sftpClient = sftp.connect(hostname, username, raw_password, port)
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
  if not operation.start():
    raise OperationError(_("Restore failed!"))
  print('\n')

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
  print(_("*** Running restore of local test backup %s" % setName))
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
  if not operation.start():
    raise OperationError(_("Restore failed!"))
  print('\n')

# Local archive
print(_("*** Running restore of a local archive"))
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
if not operation.start():
  raise OperationError(_("Restore failed!"))
print('\n')

# Local folder
print(_("*** Running restore of a local folder"))
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
if not operation.start():
  raise OperationError(_("Restore failed!"))
print('\n')

# Remote archive (SSH)
print(_("*** Running restore of a remote archive (SSH)"))
name = "restore-remote-archive (SSH)"
restoreDestination = os.path.join(DESTDIR_RESTORE, name)
options = {}
options["Destination"] = restoreDestination
options["RemoteHost"] = hostname
options["RemotePassword"] = password
options["RemotePort"] = 22
options["RemoteUsername"] = username
client, sftpClient = sftp.connect(hostname, username, raw_password, port)
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
if not operation.start():
  raise OperationError(_("Restore failed!"))
print('\n')

# Remote folder (SSH)
print(_("*** Running restore of a remote folder (SSH)"))
name = "restore-remote-folder (SSH)"
restoreDestination = os.path.join(DESTDIR_RESTORE, name)
options = {}
options["Destination"] = restoreDestination
options["RemoteHost"] = hostname
options["RemotePassword"] = password
options["RemotePort"] = 22
options["RemoteUsername"] = username
client, sftpClient = sftp.connect(hostname, username, raw_password, port)
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
if not operation.start():
  raise OperationError(_("Restore failed!"))
print('\n')
