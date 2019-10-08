__author__ = 'zenzen san'
__version__ = '1.0.0'
__name__ = 'wifips'
__license__ = 'GPL3'
__description__ = """Saves a json file with the access points with more signal 
                     whenever a handshake is captured. 
                     When internet is available the files are converted in geo locations 
                     using Mozilla LocationService """

import logging
import json
import os
from urllib.request import urlopen
from datetime import datetime
from time import sleep 

URL_API_MOZILLA_LOCATION_SERVICE = 'https://location.services.mozilla.com/v1/geolocate?key='
KEY_API_MOZILLA_LOCATION_SERVICE = 'test'   

def on_loaded():
    logging.info("wifips plugin loaded. :)")

def on_internet_available(ui, keypair, config):
    try:
        for ff in os.listdir('/root/handshakes'):
            geo_file = os.path.join('/root/handshakes', ff.replace('.wifips.json','.geo.json'))
            if not os.path.isfile(geo_file):
                if ff.endswith(".wifips.json"):
                    ff = os.path.join('/root/handshakes',ff)
                    with open(ff, 'r') as fp:
                        data = fp.read()
                    geo = _get_geolocation_moz_wifips(data)
                    with open(geo_file, 'w+t') as fp:
                        fp.write(geo.decode('ascii'))
                    logging.info("wifips plugin: saving coordinates for: {}".format(ff.replace('.wifips.json','')))
                    sleep(.500)
    except Exception as e:
        logging.exception('WIFIPS PLUGIN ERROR')

def on_ready(agent):
    pass

def on_handshake(agent, filename, access_point, client_station):
    wifips = _get_wifips(agent)
    wifips_filename = filename.replace('.pcap', '.wifips.json')
    logging.info("wifips plugin: saving location to %s" % (wifips_filename))
    with open(wifips_filename, 'w+t') as fp:
        json.dump(wifips, fp)

def _get_wifips(agent):
    info = agent.session()
    aps = agent.get_access_points()
    wifips = {}
    wifips['wifiAccessPoints'] = []
    # 6 seems a good number to save a wifi networks location  
    for ap in sorted(aps,key=lambda i:i['rssi'],reverse=True)[:6]: 
        wifips['wifiAccessPoints'].append({'macAddress': ap['mac'], 'signalStrength': ap['rssi']}) 
    return wifips

def _get_geolocation_moz_wifips(post_data):
    geourl = URL_API_MOZILLA_LOCATION_SERVICE+KEY_API_MOZILLA_LOCATION_SERVICE
    try:
        response = urlopen(geourl, post_data.encode('ascii')).read()
        return response
    except Exception as e:
        logging.exception('WIFIPS PLUGIN - Something went wrong with Mozilla Location Service')

