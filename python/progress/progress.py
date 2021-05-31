import os
import threading
import datetime
import time
import random

import gi 
gi.require_version('Gtk', '3.0')  # isort:skip
from gi.repository import Gtk, Pango

pkg = 'foo-too-loo-3:2.3.0-1.fc34.noarch'

ACTIONS = [
    f"Updating: {pkg}",
    f"Updated: {pkg}",
    f"Installing: {pkg}",
    f"Reinstalling: {pkg}",
    f"Cleanup: {pkg}",
    f"Removing: {pkg}",
    f"Obsoleting: {pkg}",
    f"Downgrading: {pkg}",
    f"Verifying: {pkg}",
    f"Running scriptlet for: {pkg}"
]

STATES = [
    'Downloading packages',
    'Checking package signatures',
    'Testing Package Transactions',
    'Applying changes to the system',
    'Verify changes on the system'
]


class BuilderApp:
    def __init__(self):
        self.timer = None
        self.event = None
        self.fraction = 0.0
        
        
        self.builder = Gtk.Builder()
        filename = 'progress.ui'

        self.builder.add_from_file(filename)
        self.builder.connect_signals(self)

        window = self.builder.get_object('window')
        window.connect('destroy', lambda x: Gtk.main_quit())
        window.show_all()
        
        self.progress = self.builder.get_object('infobar_progress')
        self.msg = self.builder.get_object('infobar_label')
        self.msg_sub = self.builder.get_object('infobar_sublabel')
        self.text = self.builder.get_object('text')
        fontdesc = Pango.FontDescription("Noto Sans Condensed Regular 12")
        print(fontdesc)
        self.text.modify_font(fontdesc)

        self.start_timer()
        
    def update_progress(self):
        self.fraction += .1
        if self.fraction > 1.0:
            self.fraction = 0.0
        self.progress.set_fraction(self.fraction)

    def get_time(self):
        seconds = 0
        state = 0
        action = 0
        self.msg.set_text(STATES[state])
        pkg = 'foo-too-loo-3:2.3.0-1.fc34.noarch'
        self.msg_sub.set_text('')
        while not self.event.is_set():
            seconds += 1
            if seconds % 20 == 0:
                self.msg.set_text(STATES[state])
                state += 1
                if state == 5: state = 0
            if seconds % 5 == 0:
                self.msg_sub.set_text(ACTIONS[action])
                action += 1
                if action == 10: action = 0
            self.update_progress()
            time.sleep(1)
 
    def start_timer(self):
        print('start')
        self.timer = threading.Thread(target=self.get_time)
        self.event = threading.Event()
        self.timer.daemon=True
        self.timer.start() 
        
def main():
    app = BuilderApp()
    Gtk.main()


if __name__ == '__main__':
    main()
