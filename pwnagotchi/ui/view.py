import _thread
from threading import Lock
import time
import logging
from PIL import Image, ImageDraw

import pwnagotchi.utils as utils
import pwnagotchi.plugins as plugins
from pwnagotchi.voice import Voice

import pwnagotchi.ui.fonts as fonts
import pwnagotchi.ui.faces as faces
from pwnagotchi.ui.components import *
from pwnagotchi.ui.state import State

WHITE = 0xff
BLACK = 0x00
ROOT = None

def setup_display_specifics(config):
    width = 0
    height = 0
    face_pos = (0, 0)
    name_pos = (0, 0)
    status_pos = (0, 0)

    if config['ui']['display']['type'] in ('inky', 'inkyphat'):
        fonts.setup(10, 8, 10, 25)

        width = 212
        height = 104
        face_pos = (0, int(height / 4))
        name_pos = (int(width / 2) - 15, int(height * .15))
        status_pos = (int(width / 2) - 15, int(height * .30))

    elif config['ui']['display']['type'] in ('papirus', 'papi'):
        fonts.setup(10, 8, 10, 23)

        width = 200
        height = 96
        face_pos = (0, int(height / 4))
        name_pos = (int(width / 2) - 15, int(height * .15))
        status_pos = (int(width / 2) - 15, int(height * .30))

    elif config['ui']['display']['type'] in ('ws_1', 'ws1', 'waveshare_1', 'waveshare1',
                                             'ws_2', 'ws2', 'waveshare_2', 'waveshare2'):
        fonts.setup(10, 9, 10, 35)

        width = 250
        height = 122
        face_pos = (0, 40)
        name_pos = (125, 20)
        status_pos = (125, 35)

    return width, height, face_pos, name_pos, status_pos


class View(object):
    def __init__(self, config, state={}):
        global ROOT

        self._render_cbs = []
        self._config = config
        self._canvas = None
        self._frozen = False
        self._lock = Lock()
        self._voice = Voice(lang=config['main']['lang'])

        self._width, self._height, \
        face_pos, name_pos, status_pos = setup_display_specifics(config)

        self._state = State(state={
            'channel': LabeledValue(color=BLACK, label='CH', value='00', position=(0, 0), label_font=fonts.Bold,
                                    text_font=fonts.Medium),
            'aps': LabeledValue(color=BLACK, label='APS', value='0 (00)', position=(30, 0), label_font=fonts.Bold,
                                text_font=fonts.Medium),

            # 'epoch': LabeledValue(color=BLACK, label='E', value='0000', position=(145, 0), label_font=fonts.Bold,
            #                      text_font=fonts.Medium),

            'uptime': LabeledValue(color=BLACK, label='UP', value='00:00:00', position=(self._width - 65, 0),
                                   label_font=fonts.Bold,
                                   text_font=fonts.Medium),

            'line1': Line([0, int(self._height * .12), self._width, int(self._height * .12)], color=BLACK),
            'line2': Line(
                [0, self._height - int(self._height * .12), self._width, self._height - int(self._height * .12)],
                color=BLACK),

            'face': Text(value=faces.SLEEP, position=face_pos, color=BLACK, font=fonts.Huge),

            'friend_face': Text(value=None, position=(0, (self._height * 0.88) - 15), font=fonts.Bold, color=BLACK),
            'friend_name': Text(value=None, position=(40, (self._height * 0.88) - 13), font=fonts.BoldSmall,
                                color=BLACK),

            'name': Text(value='%s>' % 'pwnagotchi', position=name_pos, color=BLACK, font=fonts.Bold),

            'status': Text(value=self._voice.default(),
                           position=status_pos,
                           color=BLACK,
                           font=fonts.Medium,
                           wrap=True,
                           # the current maximum number of characters per line, assuming each character is 6 pixels wide
                           max_length=(self._width - status_pos[0]) // 6),

            'shakes': LabeledValue(label='PWND ', value='0 (00)', color=BLACK,
                                   position=(0, self._height - int(self._height * .12) + 1), label_font=fonts.Bold,
                                   text_font=fonts.Medium),
            'mode': Text(value='AUTO', position=(self._width - 25, self._height - int(self._height * .12) + 1),
                         font=fonts.Bold, color=BLACK),
        })

        for key, value in state.items():
            self._state.set(key, value)

        plugins.on('ui_setup', self)

        if config['ui']['fps'] > 0.0:
            _thread.start_new_thread(self._refresh_handler, ())
            self._ignore_changes = ()
        else:
            logging.warning("ui.fps is 0, the display will only update for major changes")
            self._ignore_changes = ('uptime', 'name')

        ROOT = self

    def add_element(self, key, elem):
        self._state.add_element(key, elem)

    def width(self):
        return self._width

    def height(self):
        return self._height

    def on_state_change(self, key, cb):
        self._state.add_listener(key, cb)

    def on_render(self, cb):
        if cb not in self._render_cbs:
            self._render_cbs.append(cb)

    def _refresh_handler(self):
        delay = 1.0 / self._config['ui']['fps']
        # logging.info("view refresh handler started with period of %.2fs" % delay)

        while True:
            name = self._state.get('name')
            self.set('name', name.rstrip('█').strip() if '█' in name else (name + ' █'))
            self.update()
            time.sleep(delay)

    def set(self, key, value):
        self._state.set(key, value)

    def on_starting(self):
        self.set('status', self._voice.on_starting())
        self.set('face', faces.AWAKE)

    def on_ai_ready(self):
        self.set('mode', '  AI')
        self.set('face', faces.HAPPY)
        self.set('status', self._voice.on_ai_ready())
        self.update()

    def on_manual_mode(self, log):
        self.set('mode', 'MANU')
        self.set('face', faces.SAD if log.handshakes == 0 else faces.HAPPY)
        self.set('status', self._voice.on_log(log))
        self.set('epoch', "%04d" % log.epochs)
        self.set('uptime', log.duration)
        self.set('channel', '-')
        self.set('aps', "%d" % log.associated)
        self.set('shakes', '%d (%s)' % (log.handshakes, \
                                        utils.total_unique_handshakes(self._config['bettercap']['handshakes'])))
        self.set_closest_peer(log.last_peer, log.peers)

    def is_normal(self):
        return self._state.get('face') not in (
            faces.INTENSE,
            faces.COOL,
            faces.BORED,
            faces.HAPPY,
            faces.EXCITED,
            faces.MOTIVATED,
            faces.DEMOTIVATED,
            faces.SMART,
            faces.SAD,
            faces.LONELY)

    def on_normal(self):
        self.set('face', faces.AWAKE)
        self.set('status', self._voice.on_normal())
        self.update()

    def set_closest_peer(self, peer, num_total):
        if peer is None:
            self.set('friend_face', None)
            self.set('friend_name', None)
        else:
            # ref. https://www.metageek.com/training/resources/understanding-rssi-2.html
            if peer.rssi >= -67:
                num_bars = 4
            elif peer.rssi >= -70:
                num_bars = 3
            elif peer.rssi >= -80:
                num_bars = 2
            else:
                num_bars = 1

            name = '▌' * num_bars
            name += '│' * (4 - num_bars)
            name += ' %s %d (%d)' % (peer.name(), peer.pwnd_run(), peer.pwnd_total())

            if num_total > 1:
                if num_total > 9000:
                    name += ' of over 9000'
                else:
                    name += ' of %d' % num_total

            self.set('friend_face', peer.face())
            self.set('friend_name', name)
        self.update()

    def on_new_peer(self, peer):
        self.set('face', faces.FRIEND)
        self.set('status', self._voice.on_new_peer(peer))
        self.update()

    def on_lost_peer(self, peer):
        self.set('face', faces.LONELY)
        self.set('status', self._voice.on_lost_peer(peer))
        self.update()

    def on_free_channel(self, channel):
        self.set('face', faces.SMART)
        self.set('status', self._voice.on_free_channel(channel))
        self.update()

    def wait(self, secs, sleeping=True):
        was_normal = self.is_normal()
        part = secs / 10.0

        for step in range(0, 10):
            # if we weren't in a normal state before goin
            # to sleep, keep that face and status on for
            # a while, otherwise the sleep animation will
            # always override any minor state change before it
            if was_normal or step > 5:
                if sleeping:
                    if secs > 1:
                        self.set('face', faces.SLEEP)
                        self.set('status', self._voice.on_napping(int(secs)))
                    else:
                        self.set('face', faces.SLEEP2)
                        self.set('status', self._voice.on_awakening())
                else:
                    self.set('status', self._voice.on_waiting(int(secs)))
                    if step % 2 == 0:
                        self.set('face', faces.LOOK_R)
                    else:
                        self.set('face', faces.LOOK_L)

            time.sleep(part)
            secs -= part

        self.on_normal()

    def on_shutdown(self):
        self.set('face', faces.SLEEP)
        self.set('status', self._voice.on_shutdown())
        self.update(force=True)
        self._frozen = True

    def on_bored(self):
        self.set('face', faces.BORED)
        self.set('status', self._voice.on_bored())
        self.update()

    def on_sad(self):
        self.set('face', faces.SAD)
        self.set('status', self._voice.on_sad())
        self.update()

    def on_motivated(self, reward):
        self.set('face', faces.MOTIVATED)
        self.set('status', self._voice.on_motivated(reward))
        self.update()

    def on_demotivated(self, reward):
        self.set('face', faces.DEMOTIVATED)
        self.set('status', self._voice.on_demotivated(reward))
        self.update()

    def on_excited(self):
        self.set('face', faces.EXCITED)
        self.set('status', self._voice.on_excited())
        self.update()

    def on_assoc(self, ap):
        self.set('face', faces.INTENSE)
        self.set('status', self._voice.on_assoc(ap))
        self.update()

    def on_deauth(self, sta):
        self.set('face', faces.COOL)
        self.set('status', self._voice.on_deauth(sta))
        self.update()

    def on_miss(self, who):
        self.set('face', faces.SAD)
        self.set('status', self._voice.on_miss(who))
        self.update()

    def on_lonely(self):
        self.set('face', faces.LONELY)
        self.set('status', self._voice.on_lonely())
        self.update()

    def on_handshakes(self, new_shakes):
        self.set('face', faces.HAPPY)
        self.set('status', self._voice.on_handshakes(new_shakes))
        self.update()

    def on_rebooting(self):
        self.set('face', faces.BROKEN)
        self.set('status', self._voice.on_rebooting())
        self.update()

    def on_custom(self, text):
        self.set('face', faces.DEBUG)
        self.set('status', self._voice.custom(text))
        self.update()

    def update(self, force=False):
        with self._lock:
            if self._frozen:
                return

            changes = self._state.changes(ignore=self._ignore_changes)
            if force or len(changes):
                self._canvas = Image.new('1', (self._width, self._height), WHITE)
                drawer = ImageDraw.Draw(self._canvas)

                plugins.on('ui_update', self)

                for key, lv in self._state.items():
                    lv.draw(self._canvas, drawer)

                for cb in self._render_cbs:
                    cb(self._canvas)

                self._state.reset()
