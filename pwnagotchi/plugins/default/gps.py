"""
This plugin writes the position to file if a handshake is captured
"""

import logging
import json
import os
from pwnagotchi.plugins import loaded

# Meta informations
__author__ = 'evilsocket@gmail.com'
__version__ = '1.0.0'
__name__ = 'gps'
__license__ = 'GPL3'
__description__ = 'Save GPS coordinates whenever an handshake is captured.'

# Variables
OPTIONS = dict()
PLUGIN = loaded[os.path.basename(__file__).replace(".py","")]


def on_loaded():
    PLUGIN.running = False
    logging.info("gps plugin loaded for %s", OPTIONS['device'])


def on_ready(agent):
    if os.path.exists(OPTIONS['device']):
        logging.info("enabling gps bettercap's module for %s", OPTIONS['device'])

        try:
            agent.run('gps off')
        except Exception as gps_err:
            logging.error(gps_err)

        agent.run('set gps.device %s' % OPTIONS['device'])
        agent.run('set gps.speed %d' % OPTIONS['speed'])
        agent.run('gps on')
        PLUGIN.running = True
    else:
        logging.warning("no GPS detected")


def on_handshake(agent, filename, access_point, client_station):
    if PLUGIN.running:
        info = agent.session()
        gps = info['gps']
        gps_filename = filename.replace('.pcap', '.gps.json')

        logging.info("saving GPS to %s (%s)", gps_filename, gps)
        with open(gps_filename, 'w+t') as gps_file:
            json.dump(gps, gps_file)
