__author__ = 'pwnagotchi [at] rossmarks [dot] uk'
__version__ = '1.0.0'
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
import ast

OPTIONS = dict()

def on_loaded():
    logging.info("[AircrackOnly] plugin loaded")

def on_handshake(agent, filename, access_point, client_station):
    display = agent._view

    result = ast.literal_eval(subprocess.run(('/usr/bin/aircrack-ng '+filename+' | gawk \'/[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}/ {printf "["} match($0, /([0-9]+) handshake/, hs) {printf hs[1] ","} /handshake)/ {printf "False"} /with PMKID/ {printf "True"} /[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}/ {print "]"}\''), shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8'))
    if result[0] > 0:
        logging.info("[AircrackOnly] contains "+str(result[0])+" handshake(s)")
    elif result[1]:
        logging.info("[AircrackOnly] contains PMKID")
    else:
        logging.info("[AircrackOnly] contains nothing useful")
        os.remove(filename)
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
