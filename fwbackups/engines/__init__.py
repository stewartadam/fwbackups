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
This file contains generic code needed for all of the engines
"""


class EngineError(Exception):
    """An Engine error"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
