__author__ = 'leont'
__version__ = '1.0.0'
__name__ = 'pawgps'
__license__ = 'GPL3'
__description__ = 'Saves GPS coordinates whenever an handshake is captured. The GPS data is get from PAW on android '

'''
You need an bluetooth connection to your android phone which is running PAW server with the GPS "hack" from Systemic:
https://raw.githubusercontent.com/systemik/pwnagotchi-bt-tether/master/GPS-via-PAW
'''

import logging
import json
import requests

OPTIONS = dict()


def on_loaded():
    logging.info("PAW-GPS loaded")
    if 'ip' not in OPTIONS or ('ip' in OPTIONS and OPTIONS['ip'] is None):
       logging.info("PAW-GPS: No IP Address in the config file is defined, it uses the default (192.168.44.1)")

def on_handshake(agent, filename, access_point, client_station):
        if 'ip' not in OPTIONS or ('ip' in OPTIONS and OPTIONS['ip'] is None):
            ip = "192.168.44.1"

        gps = requests.get('http://' + ip + '/gps.xhtml')
        gps_filename = filename.replace('.pcap', '.gps.json')

        logging.info("saving GPS to %s (%s)" % (gps_filename, gps))
        with open(gps_filename, 'w+t') as f:
            f.write(gps.text)
