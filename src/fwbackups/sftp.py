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
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
Functions for operations on remote computers
"""
import glob
import os
import paramiko
import stat

from fwbackups.const import ConvertPath
from fwbackups.i18n import _

def connect(host, username, password, port=22, timeout=120):
  """Opens a SSH connection and returns the SFTP client object"""
  port = int(port)
  client = paramiko.SSHClient()
  client.load_system_host_keys()
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  client.connect(host, port, username, password, timeout=timeout)
  try:
    transport = client.get_transport()
    transport.use_compression(True)
  except: # < v1.7.2 - no compression support
    pass
  sftp = client.open_sftp()
  return client, sftp

def exists(sftp, path):
  """Determines if path on remote host exists"""
  try:
    sftp.stat(path)
    return True
  except IOError, errorDesc:
    return False

def isFolder(sftp, path):
  """Determines if path on remote host is a folder"""
  if not exists:
    return False
  try:
    mode = sftp.lstat(path).st_mode
  except os.error:
    mode = 0 # so below returns False
  return stat.S_ISDIR(mode)

def mkdir_p(sftp, folder):
  """Creates a folder, and all its parents, on the remote server"""
  path, name = os.path.split(folder)
  if not exists(sftp, path):
    mkdir_p(sftp, path)
  if not exists(sftp, folder):
    sftp.mkdir(folder)
  return True

def remove(sftp, path):
  """Removes file or folder path from the server"""
  if not exists(sftp, path):
    return False
  if isFolder(sftp, path):
    return rmtree(sftp, path)
  else:
    return sftp.remove(path)

def rmtree(sftp, folder):
  """Remove folder on remote host recursively"""
  for name in sftp.listdir(folder):
    fullpath = os.path.join(folder, name)
    if isFolder(sftp, fullpath):
      rmtree(sftp, fullpath)
    else:
      sftp.remove(fullpath)
  sftp.rmdir(folder)

def receive(sftp, src, dst):
  """Calls recieveFile or recieveFolder depending on 'src' (remote).
  WARNING: receiveFolder isn't implemented yet."""
  if not exists(sftp, src):
    return False
  if isFolder(sftp, src):
    return receiveFolder(sftp, src, dst)
  else:
    return receiveFile(sftp, src, dst)

def receiveFile(sftp, src, dst):
  """Gets src (remote) to dest (local)."""
  # open sftp, download then close
  sftp.get(src, dst)
  return True

def receiveFolder(sftp, src, dst):
  """Not implemented yet - for a future release"""
  print 'Warning: receiveFolder() has not been implemented yet.'
  return -1

def put(sftp, src, dst, symlinks=False, excludes=[]):
  """Transfers the local file or folder src to folder dst on the remote host."""
  mkdir_p(sftp, dst)
  if not isFolder(sftp, dst):
    return False
  if os.path.isdir(src):
    putFolder(sftp, src, dst, symlinks, excludes)
  elif os.path.isfile(src):
    putFile(sftp, src, dst, symlinks, excludes)
  else:
    return False
  return True

# The following glob-related functions are a slightly modified version of the
# Python module glob.py included in Python 2.5.2 to work with any directory.
# Original file is Copyright (c) 2001 - 2006 Python Software Foundation.

def iglob(pattern, folder):
  if not glob.has_magic(pattern): # nothing to expand
    pattern2 = os.path.normpath(folder+os.sep+pattern) # make relative to folder
    if os.path.lexists(pattern):
      yield pattern
    elif os.path.lexists(pattern2):
      yield pattern2
    return
  dirname, basename = os.path.split(pattern)
  if not dirname:
    for name in glob.glob1(folder, basename):
      yield os.path.normpath(folder+os.sep+name)
    return
  if glob.has_magic(dirname):
    dirs = iglob(dirname)
  else:
    dirs = [dirname]
  if glob.has_magic(basename):
    glob_in_dir = glob.glob1
  else:
    glob_in_dir = glob.glob0
  for dirname in dirs:
    for name in glob_in_dir(dirname, basename):
      yield os.path.join(dirname, name)

def myglob(pattern, folder):
  # generator --> list
  return list(iglob(pattern, folder))

def putFile(sftp, src, dst, symlinks=False, excludes=[]):
  """Moves src (local) to dst (remote). Assumes dst exists and is a folder"""
  for exclude in excludes:
    if src in myglob(exclude, os.path.dirname(src)):
      return True
  # open sftp, upload then close
  if symlinks and os.path.islink(src):
    linkto = os.readlink(src)
    return sftp.symlink(linkto, dst)
  else:
    return sftp.put(src, os.path.join(dst, os.path.basename(src)) )

def putFolder(sftp, src, dst, symlinks=False, excludes=[]):
  """Copies src (local) to dst (remote). Folder dst will be created"""
  # Check if the src itself is an exclude
  # FIXME: This means we check any subdirectory against excludes 2x
  SKIPME = 0
  for exclude in excludes: # excludes pattern matching
    if src in myglob(exclude, os.path.dirname(src)):
      SKIPME = 1
      break # it is pointless to process further excludes
  if SKIPME:
    return
  errors = []
  sftp.chdir(dst)
  dst = os.path.join(dst, os.path.basename(src))
  if not exists(sftp, dst):
    sftp.mkdir(dst)
  sftp.chdir(dst)
  for item in os.listdir(src):
    # make absolute paths
    src_abs =  os.path.join(src, item)
    dst_abs = os.path.join(dst, item)
    SKIPME = 0
    for exclude in excludes: # excludes pattern matching
      if src_abs in myglob(exclude, os.path.dirname(src_abs)):
        SKIPME = 1
        break # it is pointless to process further excludes
    if SKIPME:
      continue
    try:
      # at this point, excludes have been handled and we're ready to copy.
      if symlinks and os.path.islink(src_abs):
        linkto = os.readlink(src_abs)
        #sftp.symlink(abs_src, rel_dst)
        sftp.symlink(linkto, item)
      elif os.path.isdir(src_abs):
        # run this again in the subfolder
        putFolder(sftp, src_abs, dst, symlinks, excludes)
      elif os.path.isfile(src_abs):
        sftp.put(src_abs, item)
      else:
        print _('`%s\' is not a file, folder or link! Skipping.') % src_abs
    except (IOError, os.error), reason:
      # don't halt the entire copy, just print the errors at the end
      errors.append('%s --> %s: %s' % (src_abs, dst_abs, reason))
  if errors:
    print _('Could not copy some files due to errors:')
    print ''.join(errors)

# Remember we wrap this in callbacks.py
def testConnection(host, username, password, port, path):
  """Tests connecting to a SSH/SFTP connection with the supplied arguments.
  Returns True if connection was successful."""
  client, sftp = connect(host, username, password, port, timeout=30)
  doesExist = isFolder(sftp, path)
  sftp.close()
  client.close()
  return doesExist
