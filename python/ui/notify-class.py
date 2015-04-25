#!/usr/bin/python3

# 
# test of python notification class
#

from gi.repository import Gtk, GObject, Notify


class Notification(GObject.GObject):
    __gsignals__ = {
        'notify-action': (GObject.SIGNAL_RUN_FIRST, None,
                      (str,))
    }

    def __init__(self, summary, body):
        GObject.GObject.__init__(self)
        Notify.init('Yum Extender')
        icon = "yumex-dnf"
        self.notification = Notify.Notification.new(summary, body, icon)
        self.notification.set_timeout(5000)  # timeout 5s
        self.notification.add_action('open', 'Open Yum Extender', self.callback)
        self.notification.add_action('apply', 'Apply Updates', self.callback)
        self.notification.connect('closed', self.on_closed)
        
    def show(self):
        self.notification.show()

    def callback(self, widget, action):
        self.emit('notify-action', action)

    def on_closed(self, widget):
        self.emit('notify-action', 'closed')
        
def main():
    notify = Notification('New Updates', '33 available updates ')
    notify.connect('notify-action', on_notify_action)
    notify.show()
    Gtk.main()
    
def on_notify_action(widget, action):
    print(action)
    Gtk.main_quit()

if __name__ == '__main__':
    main()
