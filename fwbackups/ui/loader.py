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
Common classes for interfacing with UI files
"""
from types import FunctionType

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk  # noqa: E402


class UILoader:
    """
    Helper class to automatically load UI objects by name and wire signals.
    """

    def __init__(self, filenames, signals_from=None):
        if signals_from is not None:
            handlers = {}
            # get the bound class methods for the instance passed given the methods on the type definition
            # avoids a RuntimeError introspecting properties of Gtk.* parent classes
            methods = [(ref_name, getattr(signals_from, ref_name)) for ref_name, ref in type(signals_from).__dict__.items() if isinstance(ref, (FunctionType, classmethod, staticmethod))]
            handlers.update(methods)

        self._builder = Gtk.Builder() if handlers is None else Gtk.Builder(handlers)
        for filename in filenames:
            self._builder.add_from_file(filename)

        for buildable_obj in self._builder.get_objects():
            if isinstance(buildable_obj, Gtk.Buildable):
                buildable_id = Gtk.Buildable.get_buildable_id(buildable_obj)
                if buildable_id is not None:
                    setattr(self, buildable_id, buildable_obj)
