import time
import logging
import datetime

import pwnagotchi.ui.faces as faces


def parse_rfc3339(dt):
    return datetime.datetime.strptime(dt.split('.')[0], "%Y-%m-%dT%H:%M:%S")


class Peer(object):
    def __init__(self, obj):
        now = time.time()
        just_met = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.first_met = parse_rfc3339(obj.get('met_at', just_met))
        self.first_seen = parse_rfc3339(obj.get('detected_at', just_met))
        self.prev_seen = parse_rfc3339(obj.get('prev_seen_at', just_met))
        self.last_seen = now  # should be seen_at
        self.encounters = obj.get('encounters', 0)
        self.session_id = obj.get('session_id', '')
        self.last_channel = obj.get('channel', 1)
        self.rssi = obj.get('rssi', 0)
        self.adv = obj.get('advertisement', {})

    def update(self, new):
        if self.name() != new.name():
            logging.info("peer %s changed name: %s -> %s" % (self.full_name(), self.name(), new.name()))

        if self.session_id != new.session_id:
            logging.info("peer %s changed session id: %s -> %s" % (self.full_name(), self.session_id, new.session_id))

        self.adv = new.adv
        self.rssi = new.rssi
        self.session_id = new.session_id
        self.last_seen = time.time()
        self.prev_seen = new.prev_seen
        self.first_met = new.first_met
        self.encounters = new.encounters

    def inactive_for(self):
        return time.time() - self.last_seen

    def first_encounter(self):
        return self.encounters == 1

    def days_since_first_met(self):
        return (datetime.datetime.now() - self.first_met).days

    def face(self):
        return self.adv.get('face', faces.FRIEND)

    def name(self):
        return self.adv.get('name')

    def identity(self):
        return self.adv.get('identity')

    def version(self):
        return self.adv.get('version')

    def pwnd_run(self):
        return int(self.adv.get('pwnd_run', 0))

    def pwnd_total(self):
        return int(self.adv.get('pwnd_tot', 0))

    def uptime(self):
        return self.adv.get('uptime', 0)

    def epoch(self):
        return self.adv.get('epoch', 0)

    def full_name(self):
        return '%s@%s' % (self.name(), self.identity())

    def is_closer(self, other):
        return self.rssi > other.rssi