__author__ = 'zenzen san'
__version__ = '1.0.0'
__name__ = 'geowifi'
__license__ = 'GPL3'
__description__ = 'Saves a json file with the access points with more signal whenever a handshake is captured. This data is usable to retrieve the geographic location using Google Geolocation API or Mozilla Location Service'

import logging
import json

def on_loaded():
    logging.info("geowifi plugin loaded. :)")

def on_handshake(agent, filename, access_point, client_station):
    info = agent.session()
    aps = agent.get_access_points()
    geowifi = _geowifi_location(aps)
    geowifi_filename = filename.replace('.pcap', '.geowifi.json')

    logging.info("saving GEOWIFI location to %s" % (geowifi_filename))
    with open(geowifi_filename, 'w+t') as fp:
        json.dump(geowifi, fp)

def _geowifi_location(aps):
    geowifi = {}
    geowifi['wifiAccessPoints'] = []
    # size seems a good number to save a wifi networks location 
    for ap in sorted(aps,key=lambda i:i['rssi'],reverse=True)[:6]:
        geowifi['wifiAccessPoints'].append({'macAddress': ap['mac'], 'signalStrength': ap['rssi']})
    return geowifi

