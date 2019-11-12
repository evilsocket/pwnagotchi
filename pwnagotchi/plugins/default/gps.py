import logging
import json
import os
import pwnagotchi.plugins as plugins


class GPS(plugins.Plugin):
    __author__ = 'evilsocket@gmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Save GPS coordinates whenever an handshake is captured.'

    def __init__(self):
        self.running = False

    def on_loaded(self):
        logging.info("gps plugin loaded for %s" % self.options['device'])

    def on_ready(self, agent):
        if os.path.exists(self.options['device']):
            logging.info("enabling bettercap's gps module for %s" % self.options['device'])
            try:
                agent.run('gps off')
            except:
                pass

            agent.run('set gps.device %s' % self.options['device'])
            agent.run('set gps.speed %d' % self.options['speed'])
            agent.run('gps on')
            self.running = True
        else:
            logging.warning("no GPS detected")

    def on_handshake(self, agent, filename, access_point, client_station):
        if self.running:
            info = agent.session()
            gps = info['gps']
            gps_filename = filename.replace('.pcap', '.gps.json')

            logging.info("saving GPS to %s (%s)" % (gps_filename, gps))
            with open(gps_filename, 'w+t') as fp:
                json.dump(gps, fp)
