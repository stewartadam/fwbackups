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
import os
import paramiko

from fwbackups.const import ConvertPath
from fwbackups.i18n import _

def connect(host, username, password, port=22, timeout=120):
  """Opens a SSH connection and returns the connection object"""
  port = int(port)
  client = paramiko.SSHClient()
  client.load_system_host_keys()
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  client.connect(host, port, username, password, timeout=timeout)
  

def listdir(client, path):
  """Lists files in remote directory specified by 'path' using 'connection'"""
  sftp = client.open_sftp()
  dirlisting = sftp.listdir(path)
  sftp.close()
  return dirlisting
  
def receiveFile(client, src, dst):
  """Opens a SFTP connection and gets src (remote) to dest (local)."""
  # open sftp, download then close
  sftp = client.open_sftp()
  sftp.get(src, dst)
  sftp.close()
  return True

def receiveFolder(client, src, dst):
  """Not implemented yet - for a future release"""
  print 'Warning: receiveFolder() has not been implemented yet.'
  return -1

def receive(client, src, dst):
  """Calls recieveFile or recieveFolder depending on 'src' (remote).
  WARNING: receiveFolder isn't implemented yet."""
  sftp = client.open_sftp()
  # Paramiko has no way of telling if a path is a file or folder on the remote
  # server! Use open().read(1) to determine folder/file, and stat to determine
  # if it exists instead.
  try:
    sftp.stat(src)
    exists = True
  except IOError, errorDesc:
    # no such file.
    exists = False
  if exists:
    try:
      fh = sftp.open(src)
      fh.read(1)
      isdir = False
    except Exception, error:
      isdir = False
    fh.close()
  sftp.close()
  if not exists:
    return False
  if isdir:
    return receiveFolder(client, src, dst)
  else:
    return receiveFile(client, src, dst)

def transferFile(client, src, dst):
  """Opens a SFTP connections and moves src (local) to
  dest (remote). Assumes dst is a folder and already exists."""
  port = int(port)
  # open sftp, upload then close
  sftp = client.open_sftp()
  sftp.put(src, dst)
  sftp.close()

def transferFolder(client, src, dst, symlinks=False):
  """Opens a SFTP connections and copies _contents of_ src (local) to
  dest (remote). dst will be created as a folder."""
  port = int(port)
  try:
    transport = client.get_transport()
    transport.use_compression(True)
  except:
    # 1.7.2 isn't installed - no compression support
    pass
  client.load_system_host_keys()
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  client.connect(host, port, username, password, timeout=30)
  # open sftp, upload then close
  sftp = client.open_sftp()
  errors = []
  try:
    #print 'chdir ' + os.path.dirname(dst)
    #sftp.chdir(dst)
    for dirpath, dirnames, filenames in os.walk(src):
      fullpath = os.path.join(src, dirpath)
      #print 'mkdir ' + ConvertPath('%s/%s' % (dst, dirpath.replace(src, '')))
      sftp.mkdir(ConvertPath('%s/%s' % (dst, dirpath.replace(src, ''))))
      #print 'chdir ', ConvertPath('%s/%s' % (dst, dirpath.replace(src, '')))
      sftp.chdir(ConvertPath('%s/%s' % (dst, dirpath.replace(src, ''))))
      for filename in filenames:
        fullfilename = os.path.join(fullpath, filename)
        try:
          if symlinks and os.path.islink(fullfilename):
            linkto = os.readlink(fullfilename)
            #dbg print 'linking %s to %s' % (linkto, filename)
            sftp.symlink(linkto, filename)
          elif not os.path.isfile(fullfilename):
            print _('`%s\' isn\'t a file, folder or link! Skipping.') % fullfilename
          else: # file
            #dbg print 'putting %s to %s' % (fullfilename, filename)
            sftp.put(fullfilename, os.path.split(filename)[1])
        except (IOError, os.error), reason:
          errors.append('%s --> %s: %s' % (fullfilename, os.path.split(filename)[1], reason))
      if errors:
        print _('Couldn\'t copy some files due to errors:')
        print ''.join(errors)
      #dbg print '***'
  except:
    sftp.close()
    client.close()
    raise  
  sftp.close()

# Remember we wrap this in callbacks.py
def testConnection(host, username, password, port, path):
  """Tests connecting to a SSH/SFTP connection with the supplied arguments.
  Returns True if connection was successful."""
  if not path:
    return False
  client = connect(host, username, password, port, timeout=30)
  sftp = client.open_sftp()
  try:
    sftp.stat(path)
    exists = True
  except IOError, errorDesc:
    # no such file.
    exists = False
  sftp.close()
  client.close()
  return exists


