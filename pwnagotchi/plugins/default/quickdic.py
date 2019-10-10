__author__ = 'pwnagotchi [at] rossmarks [dot] uk'
__version__ = '1.0.0'
__name__ = 'quickdic'
__license__ = 'GPL3'
__description__ = 'Run a quick dictionary scan against captured handshakes'

'''
Aircrack-ng needed, to install:
>apt-get install aircrak-ng
Upload worrdlists files in .txt forrmat to folder in config file (default: /opt/wordlists/)
'''

import logging
import subprocess
import string
import re

OPTIONS = dict()

def on_loaded():
    logging.info("Quick dictionary check plugin loaded")

def on_handshake(agent, filename, access_point, client_station):
    display = agent._view

    result = subprocess.run(('/usr/bin/aircrack-ng '+ filename +' | grep "1 handshake" | awk \'{print $2}\''),shell=True, stdout=subprocess.PIPE)
    result = result.stdout.decode('utf-8').translate({ord(c) :None for c in string.whitespace})
    if not result:
        logging.info("[quickdic] No handshake")
    else:
        logging.info("[quickdic] Handshake confirmed")
        result2 = subprocess.run(('aircrack-ng -w '+OPTIONS['wordlist_folder']+'*.txt -q -b '+result+' '+filename+' | grep KEY'),shell=True,stdout=subprocess.PIPE)
        result2 = result2.stdout.decode('utf-8').strip()
        logging.info("[quickdic] "+result2)
        if result2 != "KEY NOT FOUND":
            key = re.search('\[(.*)\]', result2)
            pwd = str(key.group(1))
            set_text("Cracked password: "+pwd)
            agent.set_excited()
            display.update(force=True)

text_to_set = "";
def set_text(text):
    global text_to_set
    text_to_set = text
    logging.info('[quickdic] setText: '+text)

def on_ui_update(ui):
    global text_to_set
    if text_to_set:
        logging.info('[quickdic] ui_update: '+text_to_set)
        ui.set('status', text_to_set)
        text_to_set = ""