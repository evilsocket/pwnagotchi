import _thread
from threading import Lock
import time
from PIL import Image, ImageDraw

import core
import pwnagotchi
from pwnagotchi import voice

import pwnagotchi.ui.fonts as fonts
import pwnagotchi.ui.faces as faces
from pwnagotchi.ui.components import *
from pwnagotchi.ui.state import State

WHITE = 0xff
BLACK = 0x00
WIDTH = 122
HEIGHT = 250


class View(object):
    def __init__(self, config, state={}):
        self._render_cbs = []
        self._config = config
        self._canvas = None
        self._lock = Lock()
        self._state = State(state={
            'channel': LabeledValue(color=BLACK, label='CH', value='00', position=(0, 0), label_font=fonts.Bold,
                                    text_font=fonts.Medium),
            'aps': LabeledValue(color=BLACK, label='APS', value='0 (00)', position=(30, 0), label_font=fonts.Bold,
                                text_font=fonts.Medium),
            #'epoch': LabeledValue(color=BLACK, label='E', value='0000', position=(145, 0), label_font=fonts.Bold,
            #                      text_font=fonts.Medium),
            'uptime': LabeledValue(color=BLACK, label='UP', value='00:00:00', position=(185, 0), label_font=fonts.Bold,
                                   text_font=fonts.Medium),

            # 'square':  Rect([1, 11, 124, 111]),
            'line1': Line([0, 13, 250, 13], color=BLACK),
            'line2': Line([0, 109, 250, 109], color=BLACK),

            # 'histogram': Histogram([4, 94], color = BLACK),

            'face': Text(value=faces.SLEEP, position=(0, 40), color=BLACK, font=fonts.Huge),

            'friend_face': Text(value=None, position=(0, 90), font=fonts.Bold, color=BLACK),
            'friend_name': Text(value=None, position=(40, 93), font=fonts.BoldSmall, color=BLACK),

            'name': Text(value='%s>' % 'pwnagotchi', position=(125, 20), color=BLACK, font=fonts.Bold),
            # 'face2':   Bitmap( '/root/pwnagotchi/data/images/face_happy.bmp', (0, 20)),
            'status': Text(value=voice.default(), position=(125, 35), color=BLACK, font=fonts.Medium),

            'shakes': LabeledValue(label='PWND ', value='0 (00)', color=BLACK, position=(0, 110), label_font=fonts.Bold,
                                   text_font=fonts.Medium),
            'mode': Text(value='AUTO', position=(225, 110), font=fonts.Bold, color=BLACK),
        })

        for key, value in state.items():
            self._state.set(key, value)

        _thread.start_new_thread(self._refresh_handler, ())

    def on_state_change(self, key, cb):
        self._state.add_listener(key, cb)

    def on_render(self, cb):
        if cb not in self._render_cbs:
            self._render_cbs.append(cb)

    def _refresh_handler(self):
        delay = 1.0 / self._config['ui']['fps']
        # core.log("view refresh handler started with period of %.2fs" % delay)

        while True:
            name = self._state.get('name')
            self.set('name', name.rstrip('█').strip() if '█' in name else (name + ' █'))
            self.update()
            time.sleep(delay)

    def set(self, key, value):
        self._state.set(key, value)

    def on_starting(self):
        self.set('status', voice.on_starting())
        self.set('face', faces.AWAKE)

    def on_ai_ready(self):
        self.set('mode', '')
        self.set('face', faces.HAPPY)
        self.set('status', voice.on_ai_ready())
        self.update()

    def on_manual_mode(self, log):
        self.set('mode', 'MANU')
        self.set('face', faces.SAD if log.handshakes == 0 else faces.HAPPY)
        self.set('status', voice.on_log(log))
        self.set('epoch', "%04d" % log.epochs)
        self.set('uptime', log.duration)
        self.set('channel', '-')
        self.set('aps', "%d" % log.associated)
        self.set('shakes', '%d (%s)' % (log.handshakes, \
                                        core.total_unique_handshakes(self._config['bettercap']['handshakes'])))
        self.set_closest_peer(log.last_peer)

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
        self.set('status', voice.on_normal())
        self.update()

    def set_closest_peer(self, peer):
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

            self.set('friend_face', peer.face())
            self.set('friend_name', name)
        self.update()

    def on_new_peer(self, peer):
        self.set('face', faces.FRIEND)
        self.set('status', voice.on_new_peer(peer))
        self.update()

    def on_lost_peer(self, peer):
        self.set('face', faces.LONELY)
        self.set('status', voice.on_lost_peer(peer))
        self.update()

    def on_free_channel(self, channel):
        self.set('face', faces.SMART)
        self.set('status', voice.on_free_channel(channel))
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
                        self.set('status', voice.on_napping(secs))
                    else:
                        self.set('face', faces.SLEEP2)
                        self.set('status', voice.on_awakening())
                else:
                    self.set('status', voice.on_waiting(secs))
                    if step % 2 == 0:
                        self.set('face', faces.LOOK_R)
                    else:
                        self.set('face', faces.LOOK_L)

            time.sleep(part)
            secs -= part

        self.on_normal()

    def on_bored(self):
        self.set('face', faces.BORED)
        self.set('status', voice.on_bored())
        self.update()

    def on_sad(self):
        self.set('face', faces.SAD)
        self.set('status', voice.on_sad())
        self.update()

    def on_motivated(self, reward):
        self.set('face', faces.MOTIVATED)
        self.set('status', voice.on_motivated(reward))
        self.update()

    def on_demotivated(self, reward):
        self.set('face', faces.DEMOTIVATED)
        self.set('status', voice.on_demotivated(reward))
        self.update()

    def on_excited(self):
        self.set('face', faces.EXCITED)
        self.set('status', voice.on_excited())
        self.update()

    def on_assoc(self, ap):
        self.set('face', faces.INTENSE)
        self.set('status', voice.on_assoc(ap))
        self.update()

    def on_deauth(self, sta):
        self.set('face', faces.COOL)
        self.set('status', voice.on_deauth(sta))
        self.update()

    def on_miss(self, who):
        self.set('face', faces.SAD)
        self.set('status', voice.on_miss(who))
        self.update()

    def on_lonely(self):
        self.set('face', faces.LONELY)
        self.set('status', voice.on_lonely())
        self.update()

    def on_handshakes(self, new_shakes):
        self.set('face', faces.HAPPY)
        self.set('status', voice.on_handshakes(new_shakes))
        self.update()

    def on_rebooting(self):
        self.set('face', faces.BROKEN)
        self.set('status', voice.on_rebooting())
        self.update()

    def update(self):
        """
         ncalls  tottime  percall  cumtime  percall filename:lineno(function)

             19    0.001    0.000    0.007    0.000 Image.py:1137(copy)
             19    0.001    0.000    0.069    0.004 Image.py:1894(rotate)
             19    0.001    0.000    0.068    0.004 Image.py:2388(transpose)
              1    0.000    0.000    0.000    0.000 Image.py:2432(ImagePointHandler)
              1    0.000    0.000    0.000    0.000 Image.py:2437(ImageTransformHandler)
             19    0.001    0.000    0.001    0.000 Image.py:2455(_check_size)
             19    0.002    0.000    0.010    0.001 Image.py:2473(new)
              1    0.002    0.002    0.127    0.127 Image.py:30(<module>)
              1    0.000    0.000    0.001    0.001 Image.py:3103(_apply_env_variables)
              1    0.000    0.000    0.000    0.000 Image.py:3139(Exif)
              1    0.000    0.000    0.000    0.000 Image.py:495(_E)
              1    0.000    0.000    0.000    0.000 Image.py:536(Image)
             76    0.003    0.000    0.003    0.000 Image.py:552(__init__)
             19    0.000    0.000    0.000    0.000 Image.py:572(size)
             57    0.004    0.000    0.006    0.000 Image.py:576(_new)
             76    0.001    0.000    0.002    0.000 Image.py:595(__exit__)
             76    0.001    0.000    0.003    0.000 Image.py:633(__del__)
              1    0.000    0.000    0.000    0.000 Image.py:71(DecompressionBombWarning)
              1    0.000    0.000    0.000    0.000 Image.py:75(DecompressionBombError)
              1    0.000    0.000    0.000    0.000 Image.py:79(_imaging_not_installed)
             95    0.002    0.000    0.014    0.000 Image.py:842(load)
             19    0.001    0.000    0.008    0.000 Image.py:892(convert)
              1    0.000    0.000    0.000    0.000 ImageColor.py:20(<module>)
            297    0.012    0.000    0.042    0.000 ImageDraw.py:101(_getink)
             38    0.001    0.000    0.026    0.001 ImageDraw.py:153(line)
            295    0.005    0.000    0.007    0.000 ImageDraw.py:252(_multiline_check)
              8    0.000    0.000    0.001    0.000 ImageDraw.py:258(_multiline_split)
        267/247    0.033    0.000    1.741    0.007 ImageDraw.py:263(text)
              8    0.003    0.000    0.237    0.030 ImageDraw.py:282(multiline_text)
             28    0.001    0.000    0.064    0.002 ImageDraw.py:328(textsize)
              1    0.000    0.000    0.008    0.008 ImageDraw.py:33(<module>)
             19    0.002    0.000    0.006    0.000 ImageDraw.py:355(Draw)
              1    0.000    0.000    0.000    0.000 ImageDraw.py:47(ImageDraw)
             19    0.002    0.000    0.004    0.000 ImageDraw.py:48(__init__)
              1    0.000    0.000    0.000    0.000 ImageFont.py:123(FreeTypeFont)
              3    0.000    0.000    0.002    0.001 ImageFont.py:126(__init__)
             28    0.001    0.000    0.062    0.002 ImageFont.py:185(getsize)
              1    0.000    0.000    0.011    0.011 ImageFont.py:28(<module>)
            259    0.020    0.000    1.435    0.006 ImageFont.py:337(getmask2)
              1    0.000    0.000    0.000    0.000 ImageFont.py:37(_imagingft_not_installed)
              1    0.000    0.000    0.000    0.000 ImageFont.py:474(TransposedFont)
              3    0.000    0.000    0.003    0.001 ImageFont.py:517(truetype)
              3    0.000    0.000    0.002    0.001 ImageFont.py:542(freetype)
              1    0.000    0.000    0.000    0.000 ImageFont.py:65(ImageFont)
              1    0.000    0.000    0.000    0.000 ImageMode.py:17(<module>)
              1    0.000    0.000    0.000    0.000 ImageMode.py:20(ModeDescriptor)
        """
        with self._lock:
            self._canvas = Image.new('1', (HEIGHT, WIDTH), WHITE)
            drawer = ImageDraw.Draw(self._canvas)

            for key, lv in self._state.items():
                lv.draw(self._canvas, drawer)

            for cb in self._render_cbs:
                cb(self._canvas)
