import time
import logging

import pwnagotchi.ui.faces as faces


class Peer(object):
    def __init__(self, obj):
        self.first_seen = time.time()
        self.last_seen = self.first_seen
        self.session_id = obj['session_id']
        self.last_channel = obj['channel']
        self.rssi = obj['rssi']
        self.adv = obj['advertisement']

    def update(self, new):
        if self.name() != new.name():
            logging.info("peer %s changed name: %s -> %s" % (self.full_name(), self.name(), new.name()))

        if self.session_id != new.session_id:
            logging.info("peer %s changed session id: %s -> %s" % (self.full_name(), self.session_id, new.session_id))

        self.adv = new.adv
        self.rssi = new.rssi
        self.session_id = new.session_id
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
