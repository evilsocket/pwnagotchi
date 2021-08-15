import logging

import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.hw.base import DisplayImpl


class OledHat(DisplayImpl):
    def __init__(self, config):
        super(OledHat, self).__init__(config, 'oledhat')
        self._display = None

    def layout(self):
        fonts.setup(8, 8, 8, 10, 10, 8)
        self._layout['width'] = 128
        self._layout['height'] = 64
        self._layout['face'] = (0, 30)
        self._layout['name'] = (0, 10)
        self._layout['channel'] = (72, 10)
        self._layout['aps'] = (0, 0)
        self._layout['uptime'] = (87, 0)
        self._layout['line1'] = [0, 9, 128, 9]
        self._layout['line2'] = [0, 54, 128, 54]
        self._layout['friend_face'] = (0, 41)
        self._layout['friend_name'] = (40, 43)
        self._layout['shakes'] = (0, 55)
        self._layout['mode'] = (107, 10)
        self._layout['status'] = {
            'pos': (37, 19),
            'font': fonts.status_font(fonts.Small),
            'max': 18
        }
        return self._layout

    def initialize(self):
        logging.info("initializing oledhat display")
        from pwnagotchi.ui.hw.libs.waveshare.oledhat.epd import EPD
        self._display = EPD()
        self._display.init()
        self._display.Clear()

    def render(self, canvas):
        self._display.display(canvas)

    def clear(self):
        self._display.clear()
