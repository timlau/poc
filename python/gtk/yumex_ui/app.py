# -*- coding: utf-8 -*-

# Sample code for use of Gtk.Application
#
# * Show how to hande cmdline in a python way
# * Show how to handle multiple starts of the application

import gi
gi.require_version('Gtk', '3.0')


import argparse
import sys

from gi.repository import Gio, Gtk, GObject


class SearchBar(GObject.GObject):
    """Handling the search UI."""

    __gsignals__ = {'search': (GObject.SignalFlags.RUN_FIRST,
                                    None,
                                    (GObject.TYPE_STRING,
                                     GObject.TYPE_STRING,
                                     GObject.TYPE_PYOBJECT,))
                    }

    FIELDS = ['name', 'summary', 'description']
    TYPES = ['prefix', 'keyword', 'fields']

    def __init__(self, win):
        GObject.GObject.__init__(self)
        self.win = win
        self.search_type = 'prefix'
        self.search_fields = ['name', 'summary']
        # widgets
        self._bar = self.win.ui('search_bar')
        # Searchbar togglebutton
        self._toggle = self.win.ui('sch_togglebutton')
        self._toggle.connect('toggled', self.on_toggle)
        # Search Entry
        self._entry = self.win.ui('search_entry')
        self._entry.connect('activate', self.on_entry_activate)
        # Search Options
        self._options = self.win.ui('search-options')
        self._options_button = self.win.ui('sch_options_button')
        self._options_button.connect('toggled', self.on_options_button)
        # setup field checkboxes
        for key in SearchBar.FIELDS:
            wid = self.win.ui('sch_fld_%s' % key)
            if key in self.search_fields:
                wid.set_active(True)
            wid.connect('toggled', self.on_fields_changed, key)
        self._set_fields_sensitive(False)
        # setup search type radiobuttons
        for key in SearchBar.TYPES:
            wid = self.win.ui('sch_opt_%s' % key)
            if key == self.search_type:
                wid.set_active(True)
            wid.connect('toggled', self.on_type_changed, key)

    def _set_fields_sensitive(self, state=True):
        """Set sensitivity of field checkboxes."""
        for key in SearchBar.FIELDS:
            wid = self.win.ui('sch_fld_%s' % key)
            wid.set_sensitive(state)

    def _get_active_field(self):
        """Get the active search fields, based on checkbox states."""
        active = []
        for key in SearchBar.FIELDS:
            wid = self.win.ui('sch_fld_%s' % key)
            if wid.get_active():
                active.append(key)
        return active

    def _set_focus(self):
        """Set focus on search entry and move cursor to end of text."""
        self._entry.grab_focus()
        self._entry.emit(
            'move-cursor', Gtk.MovementStep.BUFFER_ENDS, 1, False)

    def on_options_button(self, widget):
        """Search Option button is toggled."""
        self._options.set_reveal_child(widget.get_active())
        if not widget.get_active():
            self._set_focus()

    def on_toggle(self, widget):
        """Search Toggle button is toggled."""
        self._bar.set_search_mode(not self._bar.get_search_mode())
        if self._bar.get_search_mode():
            self._set_focus()
        else:
            # make sure search option is hidden
            self._options_button.set_active(False)

    def on_type_changed(self, widget, key):
        """Search type is changed."""
        if widget.get_active():
            self.search_type = key
            if self.search_type == 'fields':
                self._set_fields_sensitive(True)
            else:
                self._set_fields_sensitive(False)

    def on_fields_changed(self, widget, key):
        """Search fields is changed."""
        self.search_fields = self._get_active_field()

    def on_entry_activate(self, widget):
        """Seach entry is activated"""
        # make sure search option is hidden
        self._options_button.set_active(False)
        self.signal()

    def signal(self):
        """Emit a seach signal with key, search type & fields."""
        txt = self._entry.get_text()
        if self.search_type == 'fields':
            self.emit('search', txt, self.search_type, self.search_fields)
        else:
            self.emit('search', txt, self.search_type, [])


class Options(GObject.GObject):
    """Handling the mainmenu options"""

    __gsignals__ = {'option-changed': (GObject.SignalFlags.RUN_FIRST,
                                       None,
                                       (GObject.TYPE_STRING,
                                        GObject.TYPE_BOOLEAN,)
                                       )}

    OPTIONS = ['newest_only', 'clean_unused', 'clean_instonly']

    def __init__(self, win):
        GObject.GObject.__init__(self)
        self.win = win
        for key in Options.OPTIONS:
            wid = self.win.ui('option_%s' % key)
            wid.connect('toggled', self.on_toggled, key)

    def on_toggled(self, widget, flt):
        self.emit('option-changed', flt, widget.get_active())


class Filters(GObject.GObject):
    """Handling the package filter UI."""

    __gsignals__ = {'filter-changed': (GObject.SignalFlags.RUN_FIRST,
                                       None,
                                       (GObject.TYPE_STRING,)
                                       )}

    FILTERS = ['updates', 'installed', 'available', 'all']

    def __init__(self, win):
        GObject.GObject.__init__(self)
        self.win = win
        self.current = 'updates'
        for flt in Filters.FILTERS:
            wid = self.win.ui('flt_%s' % flt)
            wid.connect('toggled', self.on_toggled, flt)

    def on_toggled(self, widget, flt):
        if widget.get_active():
            self.current = flt
            self.emit('filter-changed', flt)


class Content(GObject.GObject):
    """Handling the content pages"""

    MENUS = ['packages', 'groups', 'history', 'actions']

    def __init__(self, win):
        GObject.GObject.__init__(self)
        self.win = win
        self.stack = self.win.ui('main_stack')
        self.search_toggle = self.win.ui('flt_box')
        self.filters = self.win.ui('sch_togglebutton')
        for key in Content.MENUS:
            wid = self.win.ui('main_%s' % key)
            wid.connect('activate', self.on_menu_select, key)

    def select_page(self, page):
        self.stack.set_visible_child_name(page)
        if page == 'packages':
            self.search_toggle.set_sensitive(True)
            self.filters.set_sensitive(True)
        else:
            self.search_toggle.set_sensitive(False)
            self.filters.set_sensitive(False)

    def on_menu_select(self, widget, page):
        self.select_page(page)


class Window(Gtk.ApplicationWindow):
    """Application window. """

    def __init__(self, app, gnome=True):
        Gtk.ApplicationWindow.__init__(
            self, title='Yum Extender - Powered by DNF', application=app)
        self._builder = Gtk.Builder()
        self._builder.add_from_file("test.ui")
        self.set_default_size(800, 600)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(box)
        self._headerbar = self.ui('headerbar')
        if gnome:
            self.set_titlebar(self.ui('headerbar'))
            self._headerbar.set_show_close_button(True)
        else:
            box.pack_start(self.ui('headerbar'), False, True, 0)
            self._headerbar.set_show_close_button(False)
        box.pack_start(self.ui('main_box'), False, True, 0)
        self.setup_gui()
        self.show_all()

    def ui(self, widget_name):
        return self._builder.get_object(widget_name)

    def setup_gui(self):
        # Setup search
        self.search_bar = SearchBar(self)
        self.search_bar.connect('search', self.on_search)
        # Setup package filters
        self.pkg_filter = Filters(self)
        self.pkg_filter.connect('filter-changed', self.on_filter_changed)
        # Setup Content
        self.content = Content(self)
        # Setup Options
        self.options = Options(self)
        self.options.connect('option-changed', self.on_option_changed)

    def on_search(self, widget, key, sch_type, fields):
        print(key, sch_type, fields)

    def on_filter_changed(self, widget, flt):
        print("filter changed : ", flt)

    def on_option_changed(self, widget, option, state):
        print("option changed : ", option, state)


class App(Gtk.Application):
    """Main application."""

    def __init__(self):
        Gtk.Application.__init__(self,
                    application_id="dk.yumex.yumex-ui",
                    flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)

        self.connect("activate", self.on_activate)
        self.connect("command-line", self.on_command_line)
        self.connect("shutdown", self.on_shutdown)
        self.running = False
        self.args = None
        self.dont_close = False
        self.window = None

    def on_activate(self, app):
        print("activate called")
        if not self.running:
            self.window = Window(self, gnome=True)
            app.add_window(self.window)
            self.running = True
            self.window.show()
        else:
            self.window.present()

    def on_command_line(self, app, args):
        print("on_commandline called")
        parser = argparse.ArgumentParser(prog='app')
        parser.add_argument('-d', '--debug', action='store_true')
        parser.add_argument('--exit', action='store_true')
        if not self.running:
            # First run
            self.args = parser.parse_args(args.get_arguments()[1:])
        else:
            # Second Run
            # parse cmdline in a non quitting way
            self.current_args = \
                parser.parse_known_args(args.get_arguments()[1:])[0]
            print(self.current_args)
            if self.current_args.exit:
                if self.window.can_close():
                    self.quit()
                else:
                    print("Application is busy")
        if self.args.debug:
            print(self.args)
        self.activate()
        return 0

    def on_shutdown(self, app):
        print("shutdown called")
        return 0

if __name__ == '__main__':
    app = App()
    app.run(sys.argv)