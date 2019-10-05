import time
import logging

import pwnagotchi.mesh.wifi as wifi
import pwnagotchi.ui.faces as faces


class Peer(object):
    def __init__(self, sid, channel, rssi, adv):
        self.first_seen = time.time()
        self.last_seen = self.first_seen
        self.session_id = sid
        self.last_channel = channel
        self.presence = [0] * wifi.NumChannels
        self.adv = adv
        self.rssi = rssi
        self.presence[channel - 1] = 1

    def update(self, sid, channel, rssi, adv):
        if self.name() != adv['name']:
            logging.info("peer %s changed name: %s -> %s" % (self.full_name(), self.name(), adv['name']))

        if self.session_id != sid:
            logging.info("peer %s changed session id: %s -> %s" % (self.full_name(), self.session_id, sid))

        self.presence[channel - 1] += 1
        self.adv = adv
        self.rssi = rssi
        self.session_id = sid
        self.last_seen = time.time()

    def inactive_for(self):
        return time.time() - self.last_seen

    def _adv_field(self, name, default='???'):
        return self.adv[name] if name in self.adv else default

    def face(self):
        return self._adv_field('face', default=faces.FRIEND)

    def name(self):
        return self._adv_field('name')

    def identity(self):
        return self._adv_field('identity')

    def version(self):
        return self._adv_field('version')

    def pwnd_run(self):
        return int(self._adv_field('pwnd_run', default=0))

    def pwnd_total(self):
        return int(self._adv_field('pwnd_tot', default=0))

    def uptime(self):
        return self._adv_field('uptime', default=0)

    def epoch(self):
        return self._adv_field('epoch', default=0)

    def full_name(self):
        return '%s@%s' % (self.name(), self.identity())

    def is_closer(self, other):
        return self.rssi > other.rssi
