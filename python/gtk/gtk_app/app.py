# -*- coding: utf-8 -*-

# Sample code for use of Gtk.Application
#
# * Show how to hande cmdline in a python way
# * Show how to handle multiple starts of the application

import argparse
import sys

from gi.repository import Gio, Gtk, Notify, GObject


class Notification(GObject.GObject):
    __gsignals__ = {
        'notify-action': (GObject.SIGNAL_RUN_FIRST, None,
                      (str,))
    }

    def __init__(self, summary, body):
        GObject.GObject.__init__(self)
        Notify.init('MyApp')
        icon = "dialog-warning"
        self.notification = Notify.Notification.new(summary, body, icon)
        self.notification.set_timeout(5000)  # timeout 5s
        self.notification.connect('closed', self.on_closed)

    def show(self):
        self.notification.show()

    def callback(self, widget, action):
        self.emit('notify-action', action)

    def on_closed(self, widget):
        self.emit('notify-action', 'closed')


class Window(Gtk.ApplicationWindow):
    """ Common Yumex Base window """

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(
            self, title='MyApp', application=app)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.app = app
        self._can_close = False
        self.connect('delete_event', self.on_delete_event)

    def on_delete_event(self, *args):
        print("window close event")
        return False

    def can_close(self):
        return self._can_close


class App(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self,
                    application_id="org.gnome.example",
                    flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)

        self.connect("activate", self.on_activate)
        self.connect("command-line", self.on_command_line)
        self.connect("shutdown", self.on_shutdown)
        self.running = False
        self.window = None
        self.args = None
        self.dont_close = False

    def on_activate(self, app):
        print("activate called")
        if not self.running:
            self.window = Window(app)
            app.add_window(self.window)
            self.running = True
            self.window.show()
        else:
            notify = Notification('MyApp is allready running', '')
            notify.show()
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