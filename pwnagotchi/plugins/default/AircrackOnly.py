import pwnagotchi.plugins as plugins

import logging
import subprocess
import string
import os

'''
Aircrack-ng needed, to install:
> apt-get install aircrack-ng
'''


class AircrackOnly(plugins.Plugin):
    __author__ = 'pwnagotchi [at] rossmarks [dot] uk'
    __version__ = '1.0.1'
    __license__ = 'GPL3'
    __description__ = 'confirm pcap contains handshake/PMKID or delete it'

    def __init__(self):
        super().__init__(self)
        self.text_to_set = ""

    def on_loaded(self):
        logging.info("aircrackonly plugin loaded")

    def on_handshake(self, agent, filename, access_point, client_station):
        display = agent._view
        todelete = 0
        handshakeFound = 0

        result = subprocess.run(('/usr/bin/aircrack-ng ' + filename + ' | grep "1 handshake" | awk \'{print $2}\''),
                                shell=True, stdout=subprocess.PIPE)
        result = result.stdout.decode('utf-8').translate({ord(c): None for c in string.whitespace})
        if result:
            handshakeFound = 1
            logging.info("[AircrackOnly] contains handshake")

        if handshakeFound == 0:
            result = subprocess.run(('/usr/bin/aircrack-ng ' + filename + ' | grep "PMKID" | awk \'{print $2}\''),
                                    shell=True, stdout=subprocess.PIPE)
            result = result.stdout.decode('utf-8').translate({ord(c): None for c in string.whitespace})
            if result:
                logging.info("[AircrackOnly] contains PMKID")
            else:
                todelete = 1

        if todelete == 1:
            os.remove(filename)
            self.text_to_set = "Removed an uncrackable pcap"
            display.update(force=True)

    def on_ui_update(self, ui):
        if self.text_to_set:
            ui.set('face', "(>.<)")
            ui.set('status', self.text_to_set)
            self.text_to_set = ""
