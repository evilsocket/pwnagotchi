import logging

import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.hw.base import DisplayImpl


class Waveshare213bc(DisplayImpl):
    def __init__(self, config):
        super(Waveshare213bc, self).__init__(config, 'waveshare213bc')
        self._display = None

    def layout(self):
        fonts.setup(10, 8, 10, 25, 25, 9)
        self._layout['width'] = 212
        self._layout['height'] = 104
        self._layout['face'] = (0, 26)
        self._layout['name'] = (5, 15)
        self._layout['channel'] = (0, 0)
        self._layout['aps'] = (28, 0)
        self._layout['uptime'] = (147, 0)
        self._layout['line1'] = [0, 12, 212, 12]
        self._layout['line2'] = [0, 92, 212, 92]
        self._layout['friend_face'] = (0, 76)
        self._layout['friend_name'] = (40, 78)
        self._layout['shakes'] = (0, 93)
        self._layout['mode'] = (187, 93)
        self._layout['status'] = {
            'pos': (91, 15),
            'font': fonts.status_font(fonts.Medium),
            'max': 20
        }
        return self._layout

    def initialize(self):
        logging.info("initializing waveshare 213bc display")
        from pwnagotchi.ui.hw.libs.waveshare.v213bc.epd2in13bc import EPD
        self._display = EPD()
        self._display.init()
        self._display.Clear()

    def render(self, canvas):
        buf = self._display.getbuffer(canvas)
        self._display.pwndisplay(buf)

    def clear(self):
        #pass
        self._display.pwnclear()
