__author__ = 'evilsocket@gmail.com'
__version__ = '1.0.0'
__name__ = 'gps'
__license__ = 'GPL3'
__description__ = 'Save GPS coordinates whenever an handshake is captured.'

import logging
import json
import os

running = False
OPTIONS = dict()


def on_loaded():
    logging.info("gps plugin loaded for %s" % device)


def on_ready(agent):
    global running

    if os.path.exists(device):
        logging.info("enabling gps bettercap's module for %s" % device)
        try:
            agent.run('gps off')
        except:
            pass

        agent.run('set gps.device %s' % OPTIONS['device'])
        agent.run('set gps.speed %d' % OPTIONS['speed'])
        agent.run('gps on')
        running = True
    else:
        logging.warning("no GPS detected")


def on_handshake(agent, filename, access_point, client_station):
    if running:
        info = agent.session()
        gps = info['gps']
        gps_filename = filename.replace('.pcap', '.gps.json')

        logging.info("saving GPS to %s (%s)" % (gps_filename, gps))
        with open(gps_filename, 'w+t') as fp:
            json.dump(gps, fp)
