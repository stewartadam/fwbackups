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
Python interface to 'crontab' binary
"""

import re
import subprocess
import tempfile

from fwbackups import execute
from . import const as constants

class CronError(Exception):
    """Cron interfacing error."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ValidationError(Exception):
    """Cron interfacing error."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class rawCrontabLine:
    """Represents a raw, unparsed line in the crontab"""
    __rawtext = b''

    def __init__(self, line):
        """Initialize the raw representation of the line"""
        if not isinstance(line, bytes):
            raise ValueError(f"raw crontab line expected byte input, got {type(line)} instead")
        self.__rawtext = line

    def is_comment_or_whitespace(self):
        """Returns True if the crontab entry is a comment"""
        entry_text = self.get_raw_entry_text()
        if not entry_text.strip() or entry_text.lstrip().startswith(b"#"):
            return True
        return False

    def get_raw_entry_text(self):
        """Return the raw text for the entry"""
        return self.__rawtext


class crontabLine(rawCrontabLine):
    """Parses an entry in the crontab"""
    # Initialize some variables to their default values
    __minute = None
    __hour = None
    __dayofmonth = None
    __month = None
    __dayofweek = None
    __command = None
    __end_comment = ''

    def __init__(self, minute, hour, dayofmonth, month, dayofweek, command, end_comment=''):
        """Parses the crontab entry line constructs the object"""
        self.set_all_fields(minute, hour, dayofmonth, month, dayofweek, command, end_comment)
        rawCrontabLine.__init__(self, self.get_raw_entry_text())

    def is_parsable(self):
        """Returns True if the crontab entry is parsable (comments count as parsable)"""
        if not self.is_comment_or_whitespace() \
           and None in [self.__minute, self.__hour, self.__dayofmonth,
                        self.__month, self.__dayofweek, self.__command]:
            return False
        # Basic sanity check on time fields for invalid (ie non-numeric) values
        for field in [self.__minute, self.__hour, self.__dayofmonth, self.__month, self.__dayofweek]:
            if re.compile("^[0-9/\\-,*]*$").search(field) is None:
                return False
        return True

    def get_all_fields(self):
        """Returns the fields for the crontab entry if the line was parsable.
        Otherwise, returns None."""
        if not self.is_parsable():
            raise ValueError("Entry is not parsable")
        return (self.__minute, self.__hour, self.__dayofmonth, self.__month, self.__dayofweek, self.__command, self.__end_comment)

    def set_all_fields(self, minute, hour, dayofmonth, month, dayofweek, command, end_comment=''):
        """Sets all fields in the crontab line"""
        self.__minute, self.__hour, self.__dayofmonth, self.__month, \
            self.__dayofweek, self.__command, self.__end_comment = minute, hour, \
            dayofmonth, month, dayofweek, command, end_comment or ''
        self.__rawtext = self.generate_entry_text().encode('utf-8')

    def validate(self):
        """If the entry was not parsable, a ValueError is raised."""
        if not self.is_parsable() and not self.is_comment_or_whitespace():
            raise ValueError("Entry is not parsable - cannot generate entry text")

    def generate_entry_text(self):
        """Return the generated text for the entry."""
        fields = [self.__minute, self.__hour, self.__dayofmonth, self.__month,
                  self.__dayofweek, self.__command, self.__end_comment]
        # If we're here then all fields were validated
        return ' '.join(fields).rstrip() + '\n'


def read():
    """Read in crontab entires from a crontab-formatted file. Returns a list of
    rawCrontabLine objects, one for each line."""
    # Read from the user's crontab
    retval, stdout, stderr = execute(['crontab', '-l'], stdoutfd=subprocess.PIPE, text=False)
    if retval not in [constants.EXIT_STATUS_OK, 1]:  # retval=1 happens if user does not have a crontab to remove
        raise CronError(f"Failure to remove crontab: program exited with status {retval}, {stdout.read() if stdout else ''} {stderr.read() if stderr else ''}")
    fh = stdout
    # Parse the lines
    lines = [rawCrontabLine(line) for line in fh.readlines()]
    return lines


def write(crontabEntries=[]):
    """Write a crontab-formatted file from the list of fstabLines. Return values
    of 0 or 1 to indicate a failure writing to the crontab or a success
    respectively."""
    remove()
    try:
        # We'll create a temporary file to pass to crontab as input
        fh = tempfile.NamedTemporaryFile(dir=constants.LOC, prefix='.cron-')
        path = fh.name

        for crontabEntry in crontabEntries:
            if isinstance(crontabEntry, crontabLine):  # generate the entry text
                fh.write(crontabEntry.generate_entry_text().encode("utf-8"))
            else:
                fh.write(crontabEntry.get_raw_entry_text())
        fh.flush()

        retval, stdout, stderr = execute(['crontab', path])
        if retval != constants.EXIT_STATUS_OK:
            raise CronError(f"Failure to install crontab: program exited with status {retval}, {stdout.read() if stdout else ''} {stderr.read() if stderr else ''}")
        fh.close()
    except IOError:
        return False
    return True


def remove():
    """Removes/empties a user's crontab"""
    retval, stdout, stderr = execute(['crontab', '-r'])
    if retval not in [constants.EXIT_STATUS_OK, 1]:  # retval=1 happens if user does not have a crontab to list
        raise CronError(f"Failure to read crontab: program exited with status {retval}, {stdout.read() if stdout else ''} {stderr.read() if stderr else ''}")


def clean_fwbackups_entries():
    """Reads the crontab and removes any fwbackups entries. Returns the cleaned
    lines as crontabLine objects. Does not write any changes to the crontab."""
    # Read the existing crontab
    crontabLines = read()
    # Parse each line and skip any fwbackup-related ones
    cleanedLines = []
    for line in crontabLines:
        if line.is_comment_or_whitespace():
            # Never clean out comments or whitespace
            cleanedLines.append(line)
        else:
            # if not comment or whitespace, try to parse it and see if it has our signature
            entry_text = line.get_raw_entry_text().decode('utf-8').strip()
            match = re.match(r"^([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+(.+?)\s*(#.*)?$", entry_text)
            if match is None:
                cleanedLines.append(line)
                continue
            try:
                parsedLine = crontabLine(*match.groups())
                if not parsedLine.is_parsable():
                    cleanedLines.append(line)
                    continue
                fields = parsedLine.get_all_fields()
                if entry_text.startswith('#') or not fields[6].startswith(constants.CRON_SIGNATURE):
                    cleanedLines.append(line)
            except ValueError:
                cleanedLines.append(line)
                continue
    return cleanedLines
