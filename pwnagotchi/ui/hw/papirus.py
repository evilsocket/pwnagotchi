import logging
import os

import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.hw.base import DisplayImpl


class Papirus(DisplayImpl):
    def __init__(self, config):
        super(Papirus, self).__init__(config, 'papirus')
        self._display = None

    def layout(self):
        fonts.setup(10, 8, 10, 23, 25, 9)
        self._layout['width'] = 200
        self._layout['height'] = 96
        self._layout['face'] = (0, 24)
        self._layout['name'] = (5, 14)
        self._layout['channel'] = (0, 0)
        self._layout['aps'] = (25, 0)
        self._layout['uptime'] = (135, 0)
        self._layout['line1'] = [0, 11, 200, 11]
        self._layout['line2'] = [0, 85, 200, 85]
        self._layout['friend_face'] = (0, 69)
        self._layout['friend_name'] = (40, 71)
        self._layout['shakes'] = (0, 86)
        self._layout['mode'] = (175, 86)
        self._layout['status'] = {
            'pos': (85, 14),
            'font': fonts.status_font(fonts.Medium),
            'max': 16
        }
        return self._layout

    def initialize(self):
        logging.info("initializing papirus display")
        from pwnagotchi.ui.hw.libs.papirus.epd import EPD
        os.environ['EPD_SIZE'] = '2.0'
        self._display = EPD()
        self._display.clear()

    def render(self, canvas):
        self._display.display(canvas)
        self._display.partial_update()

    def clear(self):
        self._display.clear()
