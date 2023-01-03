# -*- coding: utf-8 -*-
#  Copyright (C) 2007, 2008, 2009, 2010 Stewart Adam
#  This file is part of fwbackups.

#  fwbackups is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.

#  fwbackups is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with fwbackups; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
Common classes for interfacing with UI files
"""
import inspect
from types import FunctionType

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk  # noqa: E402


class UILoader:
  """
  Helper class to automatically load UI objects by name and wire signals.
  """
  def __init__(self, filename, signals_from=None):
    self._filename = filename
    self._objects = {}

    if signals_from is not None:
      handlers = {}
      # get the bound class methods for the instance passed given the methods on the type definition
      # avoids a RuntimeError introspecting properties of Gtk.* parent classes
      methods = [(ref_name, getattr(signals_from, ref_name)) for ref_name, ref in type(signals_from).__dict__.items() if isinstance(ref, (FunctionType, classmethod, staticmethod))]
      handlers.update(methods)

    self._builder = Gtk.Builder() if handlers is None else Gtk.Builder(handlers)
    self._builder.add_from_file(filename)

  def __getattr__(self, name: str):  # fixme: return type
    """
    Dynamically load objects from the UI file.
    """
    result = self._builder.get_object(name)
    if result is None:
      raise AttributeError(f"Cannot find widget {name} in {self._filename}.")

    # Cache the widget to speed up future lookups
    setattr(self, name, result)
    return result
