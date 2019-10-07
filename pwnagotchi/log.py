import hashlib
import time
import re
import os
from datetime import datetime

from pwnagotchi.voice import Voice
from pwnagotchi.mesh.peer import Peer
from file_read_backwards import FileReadBackwards

LAST_SESSION_FILE = '/root/.pwnagotchi-last-session'


class SessionParser(object):
    EPOCH_TOKEN = '[epoch '
    EPOCH_PARSER = re.compile(r'^.+\[epoch (\d+)\] (.+)')
    EPOCH_DATA_PARSER = re.compile(r'([a-z_]+)=([^\s]+)')
    TRAINING_TOKEN = ' training epoch '
    START_TOKEN = 'connecting to http'
    DEAUTH_TOKEN = 'deauthing '
    ASSOC_TOKEN = 'sending association frame to '
    HANDSHAKE_TOKEN = '!!! captured new handshake '
    PEER_TOKEN = 'detected unit '

    def _get_last_saved_session_id(self):
        saved = ''
        try:
            with open(LAST_SESSION_FILE, 'rt') as fp:
                saved = fp.read().strip()
        except:
            saved = ''
        return saved

    def save_session_id(self):
        with open(LAST_SESSION_FILE, 'w+t') as fp:
            fp.write(self.last_session_id)
            self.last_saved_session_id = self.last_session_id

    def _parse_datetime(self, dt):
        dt = dt.split('.')[0]
        dt = dt.split(',')[0]
        dt = datetime.strptime(dt.split('.')[0], '%Y-%m-%d %H:%M:%S')
        return time.mktime(dt.timetuple())

    def _parse_stats(self):
        self.duration = ''
        self.duration_human = ''
        self.deauthed = 0
        self.associated = 0
        self.handshakes = 0
        self.epochs = 0
        self.train_epochs = 0
        self.peers = 0
        self.last_peer = None
        self.min_reward = 1000
        self.max_reward = -1000
        self.avg_reward = 0

        started_at = None
        stopped_at = None
        cache = {}

        for line in self.last_session:
            parts = line.split(']')
            if len(parts) < 2:
                continue
            line_timestamp = parts[0].strip('[')
            line = ']'.join(parts[1:])
            stopped_at = self._parse_datetime(line_timestamp)
            if started_at is None:
                started_at = stopped_at

            if SessionParser.DEAUTH_TOKEN in line and line not in cache:
                self.deauthed += 1
                cache[line] = 1

            elif SessionParser.ASSOC_TOKEN in line and line not in cache:
                self.associated += 1
                cache[line] = 1

            elif SessionParser.HANDSHAKE_TOKEN in line and line not in cache:
                self.handshakes += 1
                cache[line] = 1

            elif SessionParser.TRAINING_TOKEN in line:
                self.train_epochs += 1

            elif SessionParser.EPOCH_TOKEN in line:
                self.epochs += 1
                m = SessionParser.EPOCH_PARSER.findall(line)
                if m:
                    epoch_num, epoch_data = m[0]
                    m = SessionParser.EPOCH_DATA_PARSER.findall(epoch_data)
                    for key, value in m:
                        if key == 'reward':
                            reward = float(value)
                            self.avg_reward += reward
                            if reward < self.min_reward:
                                self.min_reward = reward

                            elif reward > self.max_reward:
                                self.max_reward = reward

            elif SessionParser.PEER_TOKEN in line:
                m = self._peer_parser.findall(line)
                if m:
                    name, pubkey, rssi, sid, pwnd_tot, uptime = m[0]
                    if pubkey not in cache:
                        self.last_peer = Peer(sid, 1, int(rssi),
                                              {'name': name,
                                               'identity': pubkey,
                                               'pwnd_tot': int(pwnd_tot)})
                        self.peers += 1
                        cache[pubkey] = self.last_peer
                    else:
                        cache[pubkey].adv['pwnd_tot'] = pwnd_tot

        if started_at is not None:
            self.duration = stopped_at - started_at
            mins, secs = divmod(self.duration, 60)
            hours, mins = divmod(mins, 60)
        else:
            hours = mins = secs = 0

        self.duration = '%02d:%02d:%02d' % (hours, mins, secs)
        self.duration_human = []
        if hours > 0:
            self.duration_human.append('%d %s' % (hours, self.voice.hhmmss(hours, 'h')))
        if mins > 0:
            self.duration_human.append('%d %s' % (mins, self.voice.hhmmss(mins, 'm')))
        if secs > 0:
            self.duration_human.append('%d %s' % (secs, self.voice.hhmmss(secs, 's')))

        self.duration_human = ', '.join(self.duration_human)
        self.avg_reward /= (self.epochs if self.epochs else 1)

    def __init__(self, config):
        self.config = config
        self.voice = Voice(lang=config['main']['lang'])
        self.path = config['main']['log']
        self.last_session = None
        self.last_session_id = ''
        self.last_saved_session_id = ''
        self.duration = ''
        self.duration_human = ''
        self.deauthed = 0
        self.associated = 0
        self.handshakes = 0
        self.peers = 0
        self.last_peer = None
        self._peer_parser = re.compile(
            'detected unit (.+)@(.+) \(v.+\) on channel \d+ \(([\d\-]+) dBm\) \[sid:(.+) pwnd_tot:(\d+) uptime:(\d+)\]')

        lines = []

        if os.path.exists(self.path):
            with FileReadBackwards(self.path, encoding="utf-8") as fp:
                for line in fp:
                    line = line.strip()
                    if line != "" and line[0] != '[':
                        continue
                    lines.append(line)
                    if SessionParser.START_TOKEN in line:
                        break
            lines.reverse()

        if len(lines) == 0:
            lines.append("Initial Session");

        self.last_session = lines
        self.last_session_id = hashlib.md5(lines[0].encode()).hexdigest()
        self.last_saved_session_id = self._get_last_saved_session_id()

        self._parse_stats()

    def is_new(self):
        return self.last_session_id != self.last_saved_session_id
