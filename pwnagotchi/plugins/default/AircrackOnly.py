"""
Aircrack-ng needed, to install:
> apt-get install aircrack-ng
"""

import logging
import subprocess
import os

__author__ = 'pwnagotchi [at] rossmarks [dot] uk'
__version__ = '1.0.1'
__name__ = 'AircrackOnly'
__license__ = 'GPL3'
__description__ = 'confirm pcap contains handshake/PMKID or delete it'

OPTIONS = dict()


def on_loaded():
    logging.info("aircrackonly plugin loaded")

def on_handshake(agent, filename, access_point, client_station):
    ui = agent.view()
    process = subprocess.Popen(f'/usr/bin/aircrack-ng {filename} | grep -E "([^0]\d* handshake|with PMKID)"', shell=True, stdin=None,
                              stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    process.wait()
    if process.returncode > 0:
        try:
            os.remove(filename)
        except OSError as os_err:
            logging.error(os_err)
        ui.set('face', "(>.<)")
        ui.set('status', "uncrackable pcap")
        ui.update(force=True)
