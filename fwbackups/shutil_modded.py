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
Based on Python's original shutil.py file, modded to continue on errors such
as sockets. Original file Copyright (c) 2001 - 2006 Python Software Foundation

Utility functions for copying files and directory trees.
*** The functions here don't copy the resource fork or other metadata on Mac.
"""
import os
import stat
from os.path import abspath
import sys
from fwbackups.i18n import _

__all__ = ["copyfileobj", "copyfile", "copymode", "copystat", "copy", "copy2",
           "copytree", "move", "rmtree", "Error"]


class Error(EnvironmentError):
    pass


def copyfileobj(fsrc, fdst, length=16 * 1024):
    """Copy data from file-like object fsrc to file-like object fdst"""
    while True:
        buf = fsrc.read(length)
        if not buf:
            break
        fdst.write(buf)


def _samefile(src, dst):
    # Macintosh, Unix.
    if hasattr(os.path, 'samefile'):
        try:
            return os.path.samefile(src, dst)
        except OSError:
            return False

    # All other platforms: check for same pathname.
    return (os.path.normcase(os.path.abspath(src)) ==
            os.path.normcase(os.path.abspath(dst)))


def copyfile(src, dst):
    """Copy data from src to dst"""
    if _samefile(src, dst):
        raise Error("`%s` and `%s` are the same file" % (src, dst))
    fsrc = None
    fdst = None
    fsrc = open(src, 'rb')
    fdst = open(dst, 'wb')
    copyfileobj(fsrc, fdst)
    fdst.close()
    fsrc.close()


def copymode(src, dst):
    """Copy mode bits from src to dst"""
    if hasattr(os, 'chmod'):
        st = os.stat(src)
        mode = stat.S_IMODE(st.st_mode)
        os.chmod(dst, mode)


def copystat(src, dst):
    """Copy all stat info (mode bits, atime and mtime) from src to dst"""
    st = os.stat(src)
    mode = stat.S_IMODE(st.st_mode)
    if hasattr(os, 'utime'):
        os.utime(dst, (st.st_atime, st.st_mtime))
    if hasattr(os, 'chmod'):
        os.chmod(dst, mode)


def copy(src, dst):
    """Copy data and mode bits ("cp src dst")."""
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst)
    copymode(src, dst)


def copy2(src, dst):
    """Copy data and all stat info ("cp -p src dst")."""
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst)
    copystat(src, dst)


def copytree(src, dst, symlinks=False):
    """Recursively copy a directory tree using copy2().

    The destination directory must not already exist.
    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied."""
    if os.path.isdir(src):
        names = os.listdir(src)
    else:
        names = [src]
    if not os.path.exists(dst):
        os.mkdir(dst, 0o755)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        # dstname = os.path.join(dst, name)
        dstname = os.path.join(dst, os.path.split(name)[1])
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            elif not os.path.isfile(srcname):
                print(_('`%s\' isn\'t a file, folder or link! Skipping.') % srcname)
            else:
                copy2(srcname, dstname)
            # XXX What about devices, sockets etc.? Done.
        except (IOError, os.error) as why:
            errors.append('%s --> %s: %s' % (srcname, dstname, why))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.args[0])
    if errors:
        print(_('Couldn\'t copy some files due to errors:'))
        print('\n'.join(errors))
        pass


def copytree_fullpaths(src, dst, symlinks=False):
    """
    Recursively copy a directory tree using copytree().
    Use full paths - eg src of /home/admin/[files] to
    dst of /media results in /media/home/admin/[files]"""
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)
    srcDrive, srcPath = os.path.splitdrive(src)
    dstDrive, dstPath = os.path.splitdrive(dst)
    if os.path.isfile(src):
        srcPath, srcFile = os.path.split(srcPath)

    # we don't want the drive in there - tarfile doesn't do it so we won't
    # dst then append srcPath to it
    dstPath = dst + srcPath
    if not os.path.exists(dstPath):
        os.makedirs(dstPath, 0o755)
    copytree(src, dstPath, symlinks)


def rmtree(path, ignore_errors=False, onerror=None):
    """Recursively delete a directory tree.

    If ignore_errors is set, errors are ignored; otherwise, if onerror
    is set, it is called to handle the error with arguments (func,
    path, exc_info) where func is os.listdir, os.remove, or os.rmdir;
    path is the argument to that function that caused it to fail; and
    exc_info is a tuple returned by sys.exc_info().  If ignore_errors
    is false and onerror is None, an exception is raised."""
    if ignore_errors:
        def onerror(*args):
            pass
    elif onerror is None:
        def onerror(*args):
            raise
    if not os.path.isdir(path):
        try:
            os.remove(path)
            return
        except os.error as err:
            onerror(os.listdir, path, sys.exc_info())
            return

    names = []
    try:
        names = os.listdir(path)
    except os.error as err:
        onerror(os.listdir, path, sys.exc_info())
    for name in names:
        fullname = os.path.join(path, name)
        try:
            mode = os.lstat(fullname).st_mode
        except os.error:
            mode = 0
        if stat.S_ISDIR(mode):
            rmtree(fullname, ignore_errors, onerror)
        else:
            try:
                os.remove(fullname)
            except os.error as err:
                onerror(os.remove, fullname, sys.exc_info())
    try:
        os.rmdir(path)
    except os.error:
        onerror(os.rmdir, path, sys.exc_info())


def move(src, dst):
    """Recursively move a file or directory to another location.

    If the destination is on our current filesystem, then simply use
    rename.  Otherwise, copy src to the dst and then remove src.
    A lot more could be done here...  A look at a mv.c shows a lot of
    the issues this implementation glosses over."""

    try:
        os.rename(src, dst)
    except OSError:
        if os.path.isdir(src):
            if destinsrc(src, dst):
                raise Error("Cannot move a directory '%s' into itself '%s'." % (src, dst))
            copytree(src, dst, symlinks=True)
            rmtree(src)
        else:
            copy2(src, dst)
            os.unlink(src)


def destinsrc(src, dst):
    return abspath(dst).startswith(abspath(src))
