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
    __gsignals__ = {'search': (GObject.SignalFlags.RUN_FIRST,
                                    None,
                                    (GObject.TYPE_STRING,
                                     GObject.TYPE_STRING,
                                     GObject.TYPE_PYOBJECT,))
                    }

    FIELDS = ['name', 'summary', 'description']
    TYPES = ['prefix', 'keyword', 'fields']

    def __init__(self, ui):
        GObject.GObject.__init__(self)
        self.ui = ui
        self.search_type = 'prefix'
        self.search_fields = ['name', 'summary']
        # widgets
        self._bar = self.ui.get('search_bar')
        # Searchbar togglebutton
        self._toggle = self.ui.get('sch_togglebutton')
        self._toggle.connect('toggled', self.on_toggle)
        # Search Entry
        self._entry = self.ui.get('search_entry')
        self._entry.connect('activate', self.on_entry)
        # fields menu
        self._fields_menu = self.ui.get('menu_sch_opt_fields')
        self._fields_button = self.ui.get('sch_opt_field_select')
        self._fields_button.set_sensitive(False)
        for key in SearchBar.FIELDS:
            wid = self.ui.get('menu_fields_%s' % key)
            if key in self.search_fields:
                wid.set_active(True)
            wid.connect('toggled', self.on_fields_changed, key)
        # setup search type radio buttons
        for key in SearchBar.TYPES:
            wid = self.ui.get('sch_opt_%s' % key)
            if key == self.search_type:
                wid.set_active(True)
            wid.connect('toggled', self.on_type_changed, key)

    def on_toggle(self, widget):
        self._bar.set_reveal_child(widget.get_active())

    def on_type_changed(self, widget, key):
        if widget.get_active():
            self.search_type = key
            if key == 'fields':
                self._fields_button.set_sensitive(True)
            else:
                self._fields_button.set_sensitive(False)
            self.signal()

    def on_fields_changed(self, widget, key):
        self.search_fields = self._get_active_field()
        self.signal()

    def _get_active_field(self):
        active = []
        for key in SearchBar.FIELDS:
            wid = self.ui.get('menu_fields_%s' % key)
            if wid.get_active():
                active.append(key)
        return active

    def on_entry(self, widget):
        self.signal()

    def signal(self):
        txt = self._entry.get_text()
        if self.search_type == 'fields':
            self.emit('search', txt, self.search_type, self.search_fields)
        else:
            self.emit('search', txt, self.search_type, [])


class Window(Gtk.Window):
    """Custom window. """

    def __init__(self, ui, gnome=True):
        Gtk.Window.__init__(
            self, title='Yum Extender - Powered by DNF')
        self.ui = ui
        self.set_default_size(800, 600)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(box)
        if gnome:
            self.set_titlebar(self.ui.get('headerbar'))
        else:
            box.pack_start(self.ui.get('headerbar'), False, True, 0)
        box.pack_start(self.ui.get('main_box'), False, True, 0)
        self.show_all()


class UI:
    """UI Handler."""
    def __init__(self):
        self._builder = Gtk.Builder()
        self._builder.add_from_file("test.ui")
        self.window = Window(self, gnome=True)
        self.search_bar = SearchBar(self)
        self.search_bar.connect('search', self.on_search)

    def get(self, widget_name):
        return self._builder.get_object(widget_name)

    def on_search(self, widget, key, sch_type, fields):
        print(key, sch_type, fields)


class App(Gtk.Application):

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
        self.ui = UI()
        self.window = self.ui.window

    def on_activate(self, app):
        print("activate called")
        if not self.running:
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