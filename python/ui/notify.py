#!/usr/bin/python3

# test notification from python
#
#

from gi.repository import Notify, Gtk

def run_callback(widget, action):
	print("Run Callback called")
	Gtk.main_quit()
	
def quit_callback(widget, action):
	print("Quit Callback called")
	Gtk.main_quit()
	
def closed_callback(widget):
	print("notification closed")
	Gtk.main_quit()
	
Notify.init('My Application Name')
summary = 'New Updates available'
body = '33 updates ready to be install'
icon = 'yumex-dnf'
notification = Notify.Notification.new(summary, body, icon)
notification.set_timeout(10000)  # timeout 10s
notification.add_action('run', 'Run',run_callback)
notification.add_action('quit', 'Quit',quit_callback)
notification.connect('closed', closed_callback)
notification.show()
Gtk.main()
