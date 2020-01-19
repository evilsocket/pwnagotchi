import logging
import requests
import pwnagotchi.plugins as plugins

'''
You need an bluetooth connection to your android phone which is running PAW server with the GPS "hack" from Systemik and edited by shaynemk
GUIDE HERE: https://community.pwnagotchi.ai/t/setting-up-paw-gps-on-android
'''


class PawGPS(plugins.Plugin):
    __author__ = 'leont'
    __version__ = '1.0.0'
    __name__ = 'pawgps'
    __license__ = 'GPL3'
    __description__ = 'Saves GPS coordinates whenever an handshake is captured. The GPS data is get from PAW on android '

    def on_loaded(self):
        logging.info("PAW-GPS loaded")
        if 'ip' not in self.options or ('ip' in self.options and self.options['ip'] is None):
            logging.info("PAW-GPS: No IP Address in the config file is defined, it uses the default (192.168.44.1:8080)")

    def on_handshake(self, agent, filename, access_point, client_station):
        if 'ip' not in self.options or ('ip' in self.options and self.options['ip'] is None):
            ip = "192.168.44.1:8080"
        else:
            ip = self.options['ip']

        gps = requests.get('http://' + ip + '/gps.xhtml')
        gps_filename = filename.replace('.pcap', '.paw-gps.json')

        logging.info("saving GPS to %s (%s)" % (gps_filename, gps))
        with open(gps_filename, 'w+t') as f:
            f.write(gps.text)
