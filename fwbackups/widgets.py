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
Classes used by the GUI, mostly to make callbacks easier
"""
import logging
import os
import threading
import time
from xml.sax.saxutils import escape
from fwbackups.i18n import _
from . import const as constants
import fwbackups
from fwbackups import fwlogger

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk  # noqa: E402
from gi.repository import Gio  # noqa: E402
from gi.repository import Pango  # noqa: E402
from gi.repository import GLib  # noqa: E402


class TextViewConsole:
    """Encapsulate a Gtk.TextView"""

    def __init__(self, textview, default_style=None, font=None, color=None):
        """Initialize, define styles"""
        self.textview = textview
        self.buffer = self.textview.get_buffer()
        self.endMark = self.buffer.create_mark("End", self.buffer.get_end_iter(), False)
        self.startMark = self.buffer.create_mark("Start", self.buffer.get_start_iter(), False)

        # setup styles
        self.style_banner = Gtk.TextTag.new("banner")
        self.style_banner.set_property("foreground", "saddle brown")
        self.style_banner.set_property("family", "Monospace")
        self.style_banner.set_property("size_points", 8)

        self.style_ps1 = Gtk.TextTag.new("ps1")
        self.style_ps1.set_property("editable", False)
        if color:
            self.style_ps1.set_property("foreground", color)
        else:
            self.style_ps1.set_property("foreground", "DarkOrchid4")
        if font:
            self.style_ps1.set_property("font", font)
        else:
            self.style_ps1.set_property("family", "Monospace")
            self.style_ps1.set_property("size_points", 8)

        self.style_ps2 = Gtk.TextTag.new("ps2")
        self.style_ps2.set_property("foreground", "DarkOliveGreen")
        self.style_ps2.set_property("editable", False)
        self.style_ps2.set_property("font", "Monospace")

        self.style_out = Gtk.TextTag.new("stdout")
        self.style_out.set_property("foreground", "midnight blue")
        self.style_out.set_property("family", "Monospace")
        self.style_out.set_property("size_points", 8)

        self.style_err = Gtk.TextTag.new("stderr")
        self.style_err.set_property("foreground", "red")
        if font:
            self.style_err.set_property("font", font)
        else:
            self.style_err.set_property("family", "Monospace")
            self.style_err.set_property("size_points", 8)

        self.style_warn = Gtk.TextTag.new("warn")
        self.style_warn.set_property("foreground", "darkorange")
        if font:
            self.style_warn.set_property("font", font)
        else:
            self.style_warn.set_property("family", "Monospace")
            self.style_warn.set_property("size_points", 8)

        self.buffer.get_tag_table().add(self.style_banner)
        self.buffer.get_tag_table().add(self.style_ps1)
        self.buffer.get_tag_table().add(self.style_ps2)
        self.buffer.get_tag_table().add(self.style_out)
        self.buffer.get_tag_table().add(self.style_err)
        self.buffer.get_tag_table().add(self.style_warn)

        if default_style:
            self.default_style = default_style
        else:
            self.default_style = self.style_out

        # fill it with content
        self.history()

    def changeStyle(self, color, font, style=None):
        """Change the text style"""
        if not style:
            self.default_style.set_property("foreground", color)
            self.default_style.set_property("font", font)
        else:
            style.set_property("foreground", color)
            style.set_property("font", font)

    def write_line(self, txt, style=None):
        """
        Write a line to the bottom of textview and scoll to end.
          txt: Text to write
          style: (optional) Predefinded pango style to use.
        """
        start, end = self.buffer.get_bounds()
        if style is None:
            self.buffer.insert_with_tags(end, txt, self.default_style)
        else:
            self.buffer.insert_with_tags(end, txt, style)
        self.goBottom()

    def clear(self):
        self.buffer.set_text('')
        self.history()

    def goTop(self):
        self.textview.scroll_to_iter(self.buffer.get_start_iter(), 0.0, False, 0, 0)

    def goBottom(self):
        self.textview.scroll_to_iter(self.buffer.get_end_iter(), 0.0, False, 0, 0)

    def write_log_line(self, i):
        """Wrapper for write_line for log messages"""
        errType = i.split(' ')
        if len(errType) >= 5:
            if errType[4] == _('CRITICAL') or errType[4] == _('ERROR'):
                self.write_line('%s%s' % (i, os.linesep), self.style_err)
            elif errType[4] == _('WARNING'):
                self.write_line('%s%s' % (i, os.linesep), self.style_warn)
            else:
                self.write_line('%s%s' % (i, os.linesep), self.style_ps1)
        else:
            self.write_line('%s%s' % (i, os.linesep), self.style_ps1)

    def history(self):
        """Get + print all old log messages stored in the log file"""
        stream = open(constants.LOGLOC, 'r', encoding='UTF-8')
        text = stream.read()
        stream.close()
        if text.strip() != '':
            self.write_line('-- %s --%s%s' % (_('Previous log messages'), os.linesep, os.linesep), self.style_ps2)
            for i in text.split('\n'):
                self.write_log_line(i)
        else:
            self.write_line('-- %s --%s' % (_('No previous log messages to display'), os.linesep), self.style_ps2)
        self.write_line('-- %s --%s%s' % (_('Current session\'s log messages'), os.linesep, os.linesep), self.style_ps2)


class TextViewLogHandler(logging.FileHandler):
    """Python logging handler for writing in a TextViewConsole AND a file"""

    def __init__(self, console):
        logging.FileHandler.__init__(self, constants.LOGLOC)
        self.console = console
        self.history()
        self.stream = None
        self.console.write_line('-- %s --%s%s' % (_('Current session\'s log messages'), os.linesep, os.linesep), self.console.style_ps2)

    def history(self):
        """Get + print all old log messages stored in the log file"""
        stream = open(constants.LOGLOC, 'r')
        text = stream.read()
        stream.close()
        if text.strip() != '':
            self.console.write_line('-- %s --%s%s' % (_('Previous log messages'), os.linesep, os.linesep), self.console.style_ps2)
            for i in text.split(os.linesep):
                errType = i.split(' ')
                if len(errType) >= 5:
                    if errType[4] == _('CRITICAL') or errType[4] == _('ERROR'):
                        self.console.write_line('%s%s' % (i, os.linesep), self.console.style_err)
                    elif errType[4] == _('WARNING'):
                        self.console.write_line('%s%s' % (i, os.linesep), self.console.style_warn)
                    else:
                        self.console.write_line('%s%s' % (i, os.linesep), self.console.style_ps1)
                else:
                    self.console.write_line('%s%s' % (i, os.linesep), self.console.style_ps1)
        else:
            self.console.write_line('-- %s --%s' % (_('No previous log messages to display'), os.linesep), self.console.style_ps2)

    def emit(self, record):
        """Emit a message"""
        self.stream = open(constants.LOGLOC, 'a')
        msg = self.format(record)

        if self.console:
            if record.levelno < 30:
                self.console.write_line("%s\n" % msg)
            elif record.levelno == 30:
                self.console.write_line("%s\n" % msg, self.console.style_warn)
            else:
                self.console.write_line("%s\n" % msg, self.console.style_err)
        fs = "%s\n"
        try:
            self.stream.write(fs % msg)
        except UnicodeError:
            self.stream.write(fs % msg.encode("UTF-8"))
        self.flush()

    def clear(self):
        """Clear the log file and the text view"""
        self.console.clear()
        stream = open(constants.LOGLOC, 'w')
        stream.write('')
        stream.close()
        if self.stream:
            self.stream.flush()
        self.history()


class StatusBar:
    def __init__(self, widget):
        """Initialize.
          widget: GTK widget to use as the statusbar
      """
        self.statusbar = widget

    def newmessage(self, message, seconds=3):
        """New message in status bar.
          message: Message to display
          seconds: number of seconds to display the message
               defaults to three.
      """
        try:
            self.message_timeout()
        # Just means there was no existing message.
        except AttributeError:
            pass
        self.statusbar.push(1, message)
        self.message_timer = GLib.timeout_add(seconds * 1000, self.message_timeout)

    def message_timeout(self):
        """Remove a message from the statusbar"""
        self.statusbar.pop(1)
        GLib.Source.remove(self.message_timer)
        return True


class ProgressBar:
    def __init__(self, widget, ms=15):
        """Wrapper for pulsing a progressbar every 'ms' milliseconds"""
        self.progressbar = widget
        self.ms = ms
        self.pulsing = False
        self.set_pulse_step(0.01)

    def set_pulse_step(self, step):
        """Wrapper: See GTK+ help"""
        return self.progressbar.set_pulse_step(step)

    def set_fraction(self, fraction):
        """Wrapper: See GTK+ help"""
        return self.progressbar.set_fraction(fraction)

    def _pulse(self):
        """Pulse the progressbar."""
        self.progressbar.pulse()
        # Has to return true to happen again
        return True

    def startPulse(self):
        """Start auto-pulsing the progressbar"""
        if self.pulsing:
            self.stopPulse()
        self.pulsing = True
        self.pulsetimer = GLib.timeout_add(self.ms, self._pulse)

    def stopPulse(self):
        """Stop auto-pulsing the progressbar"""
        GLib.Source.remove(self.pulsetimer)
        self.progressbar.set_fraction(0)
        self.pulsing = False
        return True

    def setMs(self, ms):
        """Sets the progressbar pulse step interval"""
        self.ms = int(ms)
        if self.pulsing:
            self.stopPulse()
            self.startPulse()

    def set_text(self, text):
        """Set the progressbar's text"""
        self.progressbar.set_text(text)


class GenericDia:
    """Wrapper for the generic dialog"""

    def __init__(self, dialog, title, parent):
        """Initialize"""
        self.response = 0
        self.dialog = dialog
        self.dialog.set_title(title)
        self.dialog.set_transient_for(parent)

        self.user_responded = threading.Event()
        self.dialog.connect("response", self.on_response)

    def run(self):
        """Run the dialog"""
        self.dialog.show()
        # compat: preserve a blocking API without blocking the main UI thread now
        # that Gtk.Dialog.run() is gone
        while not self.user_responded.wait(0.01):
            doGtkEvents()
            time.sleep(0.01)
        return self.response

    def destroy(self):
        """Hide the dialog, don't kill it!"""
        self.dialog.hide()

    def runAndDestroy(self):
        """Executes run() and destroy()"""
        response = self.run()
        self.destroy()
        return response

    def on_response(self, widget, response_id):
        self.response = response_id
        self.user_responded.set()


class PathBrowser(GenericDia):
    """Wrapper for generic path dialogs"""

    def __init__(self, dialog, title, parent, ffilter=None):
        """Initialize.
          widget: The widget to use
          ffilter: List for filter creation.
              > 1st value is filter pattern
              > 2nd value is the description
      """
        GenericDia.__init__(self, dialog, title, parent)
        if ffilter:
            self.ffilter = Gtk.FileFilter()
            for pattern in ffilter[:-1]:
                self.ffilter.add_pattern(pattern)
            self.ffilter.set_name(ffilter[-1])
            self.dialog.add_filter(self.ffilter)
        else:
            self.ffilter = None

    def destroy(self):
        """Destroy the dialog and the filter"""
        GenericDia.destroy(self)
        self.dialog.destroy()

    def set_current_folder(self, path):
        """Wrapper: See GTK+ help."""
        return self.dialog.set_current_folder(path)

    def set_select_multiple(self, multipleBool):
        """Wrapper: See GTK+ help."""
        return self.dialog.set_select_multiple(multipleBool)

    def set_do_overwrite_confirmation(self, overwriteBool):
        """Wrapper: See GTK+ help."""
        return self.dialog.set_do_overwrite_confirmation(overwriteBool)

    def set_action(self, action):
        """Wrapper: See GTK+ help."""
        return self.dialog.set_action(action)

    def set_title(self, title):
        """Wrapper: See GTK+ help."""
        return self.dialog.set_title(title)

    def get_filename(self):
        """Wrapper+compat: See GTK+ help."""
        return self.dialog.get_file().get_path()

    def get_filenames(self):
        """Wrapper+compat: See GTK+ help."""
        return [gfile.get_path() for gfile in self.dialog.get_files()]

    def set_filename(self, filename):
        """Wrapper+compat: See GTK+ help."""
        return self.dialog.set_file(Gio.File.new_for_path(filename))

    def add_filter(self, ffilter):
        """Wrapper: See GTK+ help."""
        return self.dialog.add_filter(ffilter)

    def remove_filter(self, ffilter):
        """Wrapper: See GTK+ help."""
        return self.dialog.remove_filter(ffilter)


class PathDia(PathBrowser):
    """Wrapper for path selection dialog"""

    def __init__(self, dialog, title, parent, mode, ffilter=None, multiple=True):
        """Inititalize.
          mode: The gtk filebowser mode (open, save, file, etc)
          ffilter: File filter to use (see PathBrowser)
          multiple: Select multiple files or folders at once? Defaults to True
      """
        PathBrowser.__init__(self, dialog, title, parent, ffilter)
        dialog.set_action(mode)
        dialog.set_select_multiple(multiple)


class SaveDia(PathBrowser):
    """Wrapper for save dialog"""

    def __init__(self, dialog, title, parent, ffilter=None):
        """Inititalize."""
        PathBrowser.__init__(self, dialog, title, parent, ffilter)
        dialog.set_action(Gtk.FileChooserAction.SAVE)
        dialog.set_do_overwrite_confirmation(True)
        dialog.set_select_multiple(False)


class ConfirmDia(GenericDia):
    """Wrapper for confirmation dialog"""

    def __init__(self, dialog, parent, labelWidget, primaryText, secondaryText, dontShowMe=False):
        """Initialize"""
        GenericDia.__init__(self, dialog, '', parent)
        labelWidget.set_text('<span size="larger" weight="bold">%s</span>\n\n%s' % (escape(primaryText), escape(secondaryText)))
        labelWidget.set_use_markup(True)
        self.dontShowMe = dontShowMe
        if self.dontShowMe:
            self.dontShowMe.set_active(False)
            self.dontShowMe.show()

    def destroy(self):
        """Destroy the dialog, hide checkmark"""
        if self.dontShowMe:
            self.dontShowMe.hide()
        GenericDia.destroy(self)


class ErrorDia(GenericDia):
    """Wrapper for error dialog"""

    def __init__(self, dialog, parent, labelWidget, primaryText, secondaryText, dontShowMe=False):
        """Initialize"""
        GenericDia.__init__(self, dialog, '', parent)
        labelWidget.set_markup('<span size="larger" weight="bold">%s</span>\n\n%s' % (escape(primaryText), escape(secondaryText)))
        labelWidget.set_use_markup(True)


class InfoDia(GenericDia):
    """Wrapper for error dialog"""

    def __init__(self, dialog, parent, labelWidget, primaryText, secondaryText, dontShowMe=False):
        """Initialize"""
        GenericDia.__init__(self, dialog, '', parent)

        labelWidget.set_text('<span size="larger" weight="bold">%s</span>\n\n%s' % (escape(primaryText), escape(secondaryText)))
        labelWidget.set_use_markup(True)
        self.dontShowMe = dontShowMe
        if self.dontShowMe:
            self.dontShowMe.set_active(False)
            self.dontShowMe.show()

    def destroy(self):
        """Destroy the dialog, hide checkmark"""
        if self.dontShowMe:
            self.dontShowMe.hide()
        GenericDia.destroy(self)


class WarningDia(GenericDia):
    """Wrapper for warning dialog"""

    def __init__(self, dialog, parent, labelWidget, primaryText, secondaryText, dontShowMe=False):
        """Initialize"""
        GenericDia.__init__(self, dialog, '', parent)
        labelWidget.set_text('<span size="larger" weight="bold">%s</span>\n\n%s' % (escape(primaryText), escape(secondaryText)))
        labelWidget.set_use_markup(True)
        self.dontShowMe = dontShowMe
        if self.dontShowMe:
            self.dontShowMe.set_active(False)
            self.dontShowMe.show()

    def destroy(self):
        """Destroy the dialog, hide checkmark"""
        if self.dontShowMe:
            self.dontShowMe.hide()
        GenericDia.destroy(self)


class View:
    """
    Generic view class. Should be subclassed.
    """

    def _buildListstoreIndex(self, liststore, col):
        """Build a list of all values in a liststore"""
        items = []
        item = liststore.get_iter_first()
        while item is not None:
            items.append(liststore.get_value(item, col))
            item = liststore.iter_next(item)
        return items


class PathView(View):
    """Wrapper for paths in a treeview"""

    def __init__(self, treeview, statusbar, ui, parent):
        self.treeview = treeview
        self.statusbar = statusbar
        self.ui = ui
        self.parent = parent
        self.logger = fwlogger.getLogger()

        # Give it columns
        cell = Gtk.CellRendererPixbuf()
        col = Gtk.TreeViewColumn(_('Access'), cell, icon_name=0)
        col.set_resizable(True)
        self.treeview.append_column(col)

        cell = Gtk.CellRendererText()
        cell.set_property('ellipsize', Pango.EllipsizeMode.END)
        col = Gtk.TreeViewColumn(_('Path'), cell, text=1)
        col.set_resizable(True)
        self.treeview.append_column(col)

        self.liststore = Gtk.ListStore(str, str)
        self.treeview.set_model(self.liststore)
        self.treeview.set_reorderable(False)
        self.treeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

        # Just to keep things clean.
        self.clear()

    def addFile(self):
        """Add a file to the pathview"""
        widget = Gtk.FileChooserNative.new(_('Choose file(s)'), self.parent,
                                           Gtk.FileChooserAction.OPEN,
                                           _("_Open"), _("_Cancel"))
        fileDialog = PathDia(widget, _('Choose file(s)'), self.parent, Gtk.FileChooserAction.OPEN, multiple=True)
        response = fileDialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            self.add(fileDialog.get_filenames(), self._buildListstoreIndex(self.liststore, 1))
        fileDialog.destroy()

    def addFolder(self):
        """Add a folder to the pathview"""
        widget = Gtk.FileChooserNative.new(_('Choose folder(s)'), self.parent,
                                           Gtk.FileChooserAction.SELECT_FOLDER,
                                           _("_Open"), _("_Cancel"))
        fileDialog = PathDia(widget, _('Choose folder(s)'), self.parent, Gtk.FileChooserAction.SELECT_FOLDER, multiple=True)
        response = fileDialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            self.add(fileDialog.get_filenames(), self._buildListstoreIndex(self.liststore, 1))
        fileDialog.destroy()

    def add(self, paths, values):
        """Add a generic path"""
        for path in paths:
            try:
                # check if path was added already
                values.index(path)
            except ValueError:
                # path wasn't found, add it
                self.liststore.append([get_access_icon_for_path(path), path])

    def removePath(self):
        """Remote a path from the pathview"""
        try:
            model, paths = self.treeview.get_selection().get_selected_rows()
            for i in paths:
                model, paths = self.treeview.get_selection().get_selected_rows()
                model.remove(model.get_iter(paths[0]))
        except TypeError:
            self.statusbar.newmessage(_('Please select a path before choosing an action.'), 3)
            return

    def clear(self):
        self.liststore.clear()

    def load(self, config):
        for path in config.getPaths():
            self.liststore.append([get_access_icon_for_path(path), path])

    def refresh(self, config):
        self.clear()
        self.load(config)


class ExportView(View):
    """Wrapper for backup sets in a Treeview"""

    def _on_toggled(self, cell, path, model):
        """inverse toggle"""
        # rendertoggle.set_active(not rendertoggle.get_active)
        model[path][0] = not model[path][0]

    def __init__(self, treeview, statusbar, ui):
        self.treeview = treeview
        self.logger = fwlogger.getLogger()
        self.statusbar = statusbar
        self.ui = ui
        self.liststore = Gtk.ListStore(bool, str)
        # Give it columns
        cell = Gtk.CellRendererToggle()
        cell.connect('toggled', self._on_toggled, self.liststore)
        cell.set_property('activatable', True)
        col = Gtk.TreeViewColumn(_('Export'), cell, active=0)
        col.set_resizable(True)
        self.treeview.append_column(col)

        cell = Gtk.CellRendererText()
        cell.set_property('ellipsize', Pango.EllipsizeMode.END)
        col = Gtk.TreeViewColumn(_('Set'), cell, text=1)
        col.set_resizable(True)
        self.treeview.append_column(col)

        self.treeview.set_model(self.liststore)
        self.treeview.set_reorderable(False)
        # Just to keep things clean.
        self._clear()

    def _clear(self):
        """Clear all sets from the view"""
        self.liststore.clear()

    def _load(self):
        """Load all set .conf files into the view"""
        self.logger.logmsg('DEBUG', _('Parsing configuration files'))
        files = os.listdir(constants.SETLOC)
        for file in files:
            if file.endswith('.conf'):
                self.liststore.append([True, file.split('.conf')[0]])
            else:
                self.logger.logmsg('WARNING', _('Refusing to parse file `%s\': configuration files must end in `.conf\'') % file)

    def refresh(self):
        """Clears & reloads the view contents"""
        self._clear()
        self._load()


class bugReport(GenericDia):
    """Wrapper for a bug report dialog"""

    def __init__(self, dialog, textview, parent, tracebackText):
        """Uses `dialog' to show bug report `traceback' in `textview' on top
            of `parent'"""
        GenericDia.__init__(self, dialog, _('Bug Report'), parent)
        textview.get_buffer().set_text(tracebackText)


def saveFilename(parent):
    """Displays a filechooser (save) and returns the chosen filename"""
    widget = Gtk.FileChooserNative.new(_('Choose a destination'), parent,
                                       Gtk.FileChooserAction.SAVE,
                                       _("_Save"), _("_Cancel"))
    fileDialog = PathDia(widget, _('Choose file(s)'), parent, Gtk.FileChooserAction.SAVE, multiple=False)
    response = fileDialog.run()
    if response == Gtk.ResponseType.ACCEPT:
        return fileDialog.get_filename()
    else:
        filename = None
    fileDialog.destroy()
    return filename


def get_active_text(combobox):
    """
    Re-implememt the removed Gtk.Combobox.get_active_text()
    """
    if isinstance(combobox, Gtk.ComboBoxText):
        return combobox.get_active_text()
    else:
        model = combobox.get_model()
        active_iter = combobox.get_active_iter()
        return model.get_value(active_iter, 1)


def doGtkEvents():
    """Process gtk events"""
    context = GLib.MainContext.default()
    while GLib.MainContext.pending(context):
        GLib.MainContext.iteration(context)


def get_access_icon_for_path(path):
    if fwbackups.CheckPerms(path, mustExist=True):
        return 'emblem-default-symbolic'
    else:
        return 'action-unavailable-symbolic'
