import logging

import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.hw.base import DisplayImpl


class LcdHat(DisplayImpl):
    def __init__(self, config):
        super(LcdHat, self).__init__(config, 'lcdhat')
        self._display = None

    def layout(self):
        fonts.setup(10, 9, 10, 35, 25, 9)
        self._layout['width'] = 240
        self._layout['height'] = 240
        self._layout['face'] = (0, 40)
        self._layout['name'] = (5, 20)
        self._layout['channel'] = (0, 0)
        self._layout['aps'] = (28, 0)
        self._layout['uptime'] = (175, 0)
        self._layout['line1'] = [0, 14, 240, 14]
        self._layout['line2'] = [0, 108, 240, 108]
        self._layout['friend_face'] = (0, 92)
        self._layout['friend_name'] = (40, 94)
        self._layout['shakes'] = (0, 109)
        self._layout['mode'] = (215, 109)
        self._layout['status'] = {
            'pos': (125, 20),
            'font': fonts.status_font(fonts.Medium),
            'max': 20
        }

        return self._layout

    def initialize(self):
        logging.info("initializing lcdhat display")
        from pwnagotchi.ui.hw.libs.waveshare.lcdhat.epd import EPD
        self._display = EPD()
        self._display.init()
        self._display.clear()

    def render(self, canvas):
        self._display.display(canvas)

    def clear(self):
        self._display.clear()
