import logging

import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.hw.base import DisplayImpl

import os,time

class FBdev(DisplayImpl):
    def __init__(self, config):
        super(FBdev, self).__init__(config, 'spotpear24lcd')
        self._display = None

    def layout(self):
        fonts.setup(12, 10, 12, 70)
        self._layout['width'] = 320
        self._layout['height'] = 240
        self._layout['face'] = (35, 50)
        self._layout['name'] = (5, 20)
        self._layout['channel'] = (0, 0)
        self._layout['aps'] = (40, 0)
        self._layout['uptime'] = (240, 0)
        self._layout['line1'] = [0, 14, 320, 14]
        self._layout['line2'] = [0, 220, 320, 220]
        self._layout['friend_face'] = (0, 92)
        self._layout['friend_name'] = (40, 94)
        self._layout['shakes'] = (0, 220)
        self._layout['mode'] = (280, 220)
        self._layout['status'] = {
            'pos': (80, 160),
            'font': fonts.Medium,
            'max': 20
        }

        return self._layout

    def refresh(self):
        time.sleep(0.1)

    def initialize(self):
        logging.info("initializing spotpear 24inch lcd display")

    def render(self, canvas):
        canvas.rotate(180).save('/tmp/pwnagotchi.png',format='PNG')
        fbi='fbi --noverbose -a -d /dev/fb1 -T 1 /tmp/pwnagotchi.png > /dev/null 2>&1'
        os.system(fbi)
        self.refresh()

    def clear(self):
        self._display.fill((0,0,0))
        self.refresh()
