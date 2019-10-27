__author__ = 'pwnagotchi [at] rossmarks [dot] uk'
__version__ = '1.0.1'
__name__ = 'AircrackOnly'
__license__ = 'GPL3'
__description__ = 'confirm pcap contains handshake/PMKID or delete it'

'''
Aircrack-ng needed, to install:
> apt-get install aircrack-ng
'''

import logging
import subprocess
import string
import os

import pwnagotchi.ui.faces as faces

OPTIONS = dict()
FACES_LOADED = False

def on_loaded():
    logging.info("aircrackonly plugin loaded")

def on_handshake(agent, filename, access_point, client_station):
    global FACES_LOADED

    display = agent.view()
    if not FACES_LOADED:
        config = agent.config()
        faces.load_from_config(config['ui']['faces'])
        FACES_LOADED = True

    todelete = 0

    result = subprocess.run(('/usr/bin/aircrack-ng '+ filename +' | grep "1 handshake" | awk \'{print $2}\''),shell=True, stdout=subprocess.PIPE)
    result = result.stdout.decode('utf-8').translate({ord(c) :None for c in string.whitespace})
    if result:
        logging.info("[AircrackOnly] contains handshake")
    else:
        todelete = 1

    if todelete == 0:
        result = subprocess.run(('/usr/bin/aircrack-ng '+ filename +' | grep "PMKID" | awk \'{print $2}\''),shell=True, stdout=subprocess.PIPE)
        result = result.stdout.decode('utf-8').translate({ord(c) :None for c in string.whitespace})
        if result:
            logging.info("[AircrackOnly] contains PMKID")
        else:
            todelete = 1

    if todelete == 1:
        os.remove(filename)
        display.set('face', faces.SAD)
        display.set('status', "Removed an uncrackable pcap")
        display.update(force=True)
