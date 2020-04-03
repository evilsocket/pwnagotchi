import logging

import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.hw.base import DisplayImpl


class WaveshareV1(DisplayImpl):
    def __init__(self, config):
        super(WaveshareV1, self).__init__(config, 'waveshare_1')
        self._display = None

    def layout(self):
        if self.config['color'] == 'black':
            fonts.setup(10, 9, 10, 35, 25, 9)
            self._layout['width'] = 250
            self._layout['height'] = 122
            self._layout['face'] = (0, 40)
            self._layout['name'] = (5, 20)
            self._layout['channel'] = (0, 0)
            self._layout['aps'] = (28, 0)
            self._layout['uptime'] = (185, 0)
            self._layout['line1'] = [0, 14, 250, 14]
            self._layout['line2'] = [0, 108, 250, 108]
            self._layout['friend_face'] = (0, 92)
            self._layout['friend_name'] = (40, 94)
            self._layout['shakes'] = (0, 109)
            self._layout['mode'] = (225, 109)
            self._layout['status'] = {
                'pos': (125, 20),
                'font': fonts.status_font(fonts.Medium),
                'max': 20
            }
        else:
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
        if self.config['color'] == 'black':
            logging.info("initializing waveshare v1 display in monochromatic mode")
            from pwnagotchi.ui.hw.libs.waveshare.v1.epd2in13 import EPD
            self._display = EPD()
            self._display.init(self._display.lut_full_update)
            self._display.Clear(0xFF)
            self._display.init(self._display.lut_partial_update)
        elif self.config['color'] == 'fastAndFurious':
            logging.info("initializing waveshare v1 3-color display in FAST MODE")
            logging.info("THIS MAY BE POTENTIALLY DANGEROUS. NO WARRANTY IS PROVIDED")
            logging.info("USE THIS DISPLAY IN THIS MODE AT YOUR OWN RISK")
            from pwnagotchi.ui.hw.libs.waveshare.v1.epd2in13bcFAST import EPD
            self._display = EPD()
            self._display.init()
            self._display.Clear()
        else:
            logging.info("initializing waveshare v1 display 3-color mode")
            from pwnagotchi.ui.hw.libs.waveshare.v1.epd2in13bc import EPD
            self._display = EPD()
            self._display.init()
            self._display.Clear()

    def render(self, canvas):
        if self.config['color'] == 'black':
            buf = self._display.getbuffer(canvas)
            self._display.display(buf)
        elif self.config['color'] == 'fastAndFurious':
            buf_black = self._display.getbuffer(canvas)
            self._display.DisplayPartial(buf_black)
        else:
            buf_black = self._display.getbuffer(canvas)
            self._display.displayBlack(buf_black)

    def clear(self):
        self._display.Clear(0xff)
