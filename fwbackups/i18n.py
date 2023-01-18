# Copyright (C) 2023 Stewart Adam
# This file is part of fwbackups.

# fwbackups is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# fwbackups is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with fwbackups; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
This file is a slighlty modified version of the yum i18n.py file. Setups up the
fwbackups translation domain and makes _() available. Uses ugettext to make
sure translated strings are in Unicode.

New to Unicode strings? Read this page for more info:
http://boodebr.org/main/python/all-about-python-and-unicode
"""
import gettext
import locale
import sys
import unicodedata

# Set the locale according to user preference
locale.setlocale(locale.LC_ALL, '')

# NOTE: When run from Cron, some OSs (ie, Ubuntu) don't set $LANG and so we get
# garbage returned from sys.getfilesystemencoding() and locale.*
encoding = sys.getfilesystemencoding()

# If there is no locale set after setlocale(), we're probably in this situation;
# just wild guess UTF-8 and hope it's all OK. Same goes for if autodetection of
# the filesystem's encoding fails.
if None in [encoding, locale.getlocale()[1]]:
    encoding = 'utf-8'


def encode(item):
    """Takes a Unicode string and encodes the code points into a byte string using
    the determined system encoding (see above). If item is a list, the operation
    is performed to each item in the list. If the item is not a string, it is
    converted to one before applying the encoding."""
    if type(item) is list:
        return [encode(i) for i in item]
    elif type(item) is not str:
        item = str(item)
    return item.encode(encoding)


def decode(item, filename=False):
    """Takes a byte string and decodes it into a Unicode string object using the
    determined system encoding (see above). If item is a list, the operation is
    performed to each item in the list. If the item is not a string, it is
    converted to one before applying the encoding. If filename is True, then item
    will be normalized to NFC form first using the normalize() function below."""
    if type(item) is str:
        return item
    elif type(item) is list:
        return [decode(i) for i in item]
    else:
        item = str(item)
    item = item.decode(encoding)
    if filename:
        item = normalize(item)
    return item


def normalize(item):
    """This is primarily for OS X, where HFS+ stores filenames as decomposed UTF-8
    strings (there are many ways to write the same character in Unicode). This
    function will normalize Unicode string "item" so that it may be compared
    internally with other Unicode strings."""
    if not isinstance(item, str):
        item = decode(item)
    normalized = unicodedata.normalize('NFC', item)
    return normalized


try:
    _ = gettext.translation('fwbackups').ugettext
except BaseException:
    # Oops! Better return the string as it is so we don't break things
    def _(str):
        """Wrapper - returns the same string"""
        return str
