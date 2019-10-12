__author__ = 'pwnagotchi [at] rossmarks [dot] uk'
__version__ = '1.0.0'
__name__ = 'cleancap'
__license__ = 'GPL3'
__description__ = 'confirm pcap contains handshake/PMKID or delete it'

'''
Aircrack-ng needed, to install:
> apt-get install aircrack-ng
'''

import logging
import subprocess
import string
import re

OPTIONS = dict()

def on_loaded():
    logging.info("cleancap plugin loaded")

def on_handshake(agent, filename, access_point, client_station):
    display = agent._view
    todelete = 0

    result = subprocess.run(('/usr/bin/aircrack-ng '+ filename +' | grep "1 handshake" | awk \'{print $2}\''),shell=True, stdout=subprocess.PIPE)
    result = result.stdout.decode('utf-8').translate({ord(c) :None for c in string.whitespace})
    if result:
        logging.info("[cleancap] contains handshake")
    else:
        todetele = 1

    if todelete == 0:
        result = subprocess.run(('/usr/bin/aircrack-ng '+ filename +' | grep "PMKID" | awk \'{print $2}\''),shell=True, stdout=subprocess.PIPE)
        result = result.stdout.decode('utf-8').translate({ord(c) :None for c in string.whitespace})
        if result:
            logging.info("[cleancap] contains PMKID")
        else:
            todetele = 1

    if todelete == 1:
        set_text("uncrackable pcap")
        display.update(force=True)

text_to_set = "";
def set_text(text):
    global text_to_set
    text_to_set = text

def on_ui_update(ui):
    global text_to_set
    if text_to_set:
        ui.set('face', "(>.<)")
        ui.set('status', text_to_set)
        text_to_set = ""
