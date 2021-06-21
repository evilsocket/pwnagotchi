import logging

import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.hw.base import DisplayImpl

import os,time

class Waveshare35lcd(DisplayImpl):
    def __init__(self, config):
        super(Waveshare35lcd, self).__init__(config, 'waveshare35lcd')
        self._display = None

    def layout(self):
        fonts.setup(12, 10, 12, 70, 25, 9)
        self._layout['width'] = 480
        self._layout['height'] = 320
        self._layout['face'] = (110, 60)
        self._layout['name'] = (10, 30)
        self._layout['channel'] = (0, 0)
        self._layout['aps'] = (80, 0)
        self._layout['uptime'] = (400, 0)
        self._layout['line1'] = [0, 14, 480, 14]
        self._layout['line2'] = [0,300, 480, 300]
        self._layout['friend_face'] = (0, 220)
        self._layout['friend_name'] = (50, 225)
        self._layout['shakes'] = (10, 300)
        self._layout['mode'] = (440, 300)
        self._layout['status'] = {
            'pos': (80, 180),
            'font': fonts.status_font(fonts.Medium),
            'max': 100
        }

        return self._layout

    def refresh(self):
        time.sleep(0.1)

    def initialize(self):
        from pwnagotchi.ui.hw.libs.fb import fb
        self._display = fb
        logging.info("initializing waveshare 3,5inch lcd display")
        self._display.ready_fb(i=1)
        self._display.black_scr()

    def render(self, canvas):
        self._display.show_img(canvas.rotate(0))
        self.refresh()

    def clear(self):
        self._display.black_scr()
        self.refresh()
