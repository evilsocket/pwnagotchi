__author__ = 'pwnagotchi [at] rossmarks [dot] uk'
__version__ = '1.0.0'
__name__ = 'quickdic'
__license__ = 'GPL3'
__description__ = 'Run a quick dictionary scan against captured handshakes'

'''
Aircrack-ng needed, to install:
> apt-get install aircrack-ng
Upload wordlist files in .txt format to folder in config file (Default: /opt/wordlists/)
Cracked handshakes stored in handshake folder as [essid].pcap.cracked
'''

import logging
import subprocess
import string
import re

import pwnagotchi.ui.faces as faces

OPTIONS = dict()
FACES_LOADED = False

def on_loaded():
    logging.info("Quick dictionary check plugin loaded")

def on_handshake(agent, filename, access_point, client_station):
    global FACES_LOADED

    display = agent.view()
    if not FACES_LOADED:
        config = agent.config()
        faces.load_from_config(config['ui']['faces'])
        FACES_LOADED = True

    result = subprocess.run(('/usr/bin/aircrack-ng '+ filename +' | grep "1 handshake" | awk \'{print $2}\''),shell=True, stdout=subprocess.PIPE)
    result = result.stdout.decode('utf-8').translate({ord(c) :None for c in string.whitespace})
    if not result:
        logging.info("[quickdic] No handshake")
    else:
        logging.info("[quickdic] Handshake confirmed")
        result2 = subprocess.run(('aircrack-ng -w `echo '+OPTIONS['wordlist_folder']+'*.txt | sed \'s/\ /,/g\'` -l '+filename+'.cracked -q -b '+result+' '+filename+' | grep KEY'),shell=True,stdout=subprocess.PIPE)
        result2 = result2.stdout.decode('utf-8').strip()
        logging.info("[quickdic] "+result2)
        if result2 != "KEY NOT FOUND":
            key = re.search('\[(.*)\]', result2)
            pwd = str(key.group(1))

            display.set('face', faces.COOL)
            display.set("Cracked password: "+pwd)
            display.update(force=True)
