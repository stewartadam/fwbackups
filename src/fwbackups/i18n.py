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
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
This file is a slighlty modified version of the yum i18n.py file. Setups up the
fwbackups translation domain and makes _() available. Uses ugettext to make
sure translated strings are in Unicode.
"""
import gettext
import locale
import sys

# Set the locale appropriately
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
  """Encodes item with the appropriate encoding. If item is a list, the
  operation is performed to each item in the list. If the item is not a string,
  it is converted to one before applying the encoding."""
  if type(item) == list:
    return [encode(i) for i in item]
  elif type(item) not in [str, unicode]:
    item = str(item)
  return item.encode(encoding)

def decode(item):
  """Decodes item with the appropriate encoding. If item is a list, the
  operation is performed to each item in the list. If the item is not a string,
  it is converted to one before applying the encoding."""
  if type(item) == list:
    return [decode(i) for i in item]
  elif type(item) not in [str, unicode]:
    item = str(item)
  return item.decode(encoding)

try: 
  _ = gettext.translation('fwbackups').ugettext
except:
  # Oops! Better return the string as it is so we don't break things
  def _(str):
    """Wrapper - returns the same string"""
    return str