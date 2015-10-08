# -*- coding: utf-8 -*-

from gi.repository import Gtk

settings = Gtk.Settings.get_default()

print("gtk_shell_shows_app_menu :", settings.props.gtk_shell_shows_app_menu)
print("gtk-shell-shows-menubar :", settings.props.gtk_shell_shows_menubar)
