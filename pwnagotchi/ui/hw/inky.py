import logging

import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.hw.base import DisplayImpl


class Inky(DisplayImpl):
    def __init__(self, config):
        super(Inky, self).__init__(config, 'inky')
        self._display = None

    def layout(self):
        fonts.setup(10, 8, 10, 28, 25, 9)
        self._layout['width'] = 212
        self._layout['height'] = 104
        self._layout['face'] = (0, 37)
        self._layout['name'] = (5, 18)
        self._layout['channel'] = (0, 0)
        self._layout['aps'] = (30, 0)
        self._layout['uptime'] = (147, 0)
        self._layout['line1'] = [0, 12, 212, 12]
        self._layout['line2'] = [0, 92, 212, 92]
        self._layout['friend_face'] = (0, 76)
        self._layout['friend_name'] = (40, 78)
        self._layout['shakes'] = (0, 93)
        self._layout['mode'] = (187, 93)
        self._layout['status'] = {
            'pos': (102, 18),
            'font': fonts.status_font(fonts.Small),
            'max': 20
        }
        return self._layout

    def initialize(self):
        logging.info("initializing inky display")

        if self.config['color'] == 'fastAndFurious':
            logging.info("Initializing Inky in 2-color FAST MODE")
            logging.info("THIS MAY BE POTENTIALLY DANGEROUS. NO WARRANTY IS PROVIDED")
            logging.info("USE THIS DISPLAY IN THIS MODE AT YOUR OWN RISK")

            from pwnagotchi.ui.hw.libs.inkyphat.inkyphatfast import InkyPHATFast
            self._display = InkyPHATFast('black')
            self._display.set_border(InkyPHATFast.BLACK)
        elif self.config['color'] == 'auto':
            from inky.auto import auto
            self._display = auto()
            self._display.set_border(self._display.BLACK)
            self._layout['width'] = self._display.WIDTH
            self._layout['height'] = self._display.HEIGHT
        else:
            from inky import InkyPHAT
            self._display = InkyPHAT(self.config['color'])
            self._display.set_border(InkyPHAT.BLACK)

    def render(self, canvas):
        if self.config['color'] == 'black' or self.config['color'] == 'fastAndFurious':
            display_colors = 2
        else:
            display_colors = 3

        img_buffer = canvas.convert('RGB').convert('P', palette=1, colors=display_colors)
        if self.config['color'] == 'red':
            img_buffer.putpalette([
                255, 255, 255,  # index 0 is white
                0, 0, 0,  # index 1 is black
                255, 0, 0  # index 2 is red
            ])
        elif self.config['color'] == 'yellow':
            img_buffer.putpalette([
                255, 255, 255,  # index 0 is white
                0, 0, 0,  # index 1 is black
                255, 255, 0  # index 2 is yellow
            ])
        else:
            img_buffer.putpalette([
                255, 255, 255,  # index 0 is white
                0, 0, 0  # index 1 is black
            ])

        self._display.set_image(img_buffer)
        try:
            self._display.show()
        except:
            logging.exception("error while rendering on inky")

    def clear(self):
        self._display.Clear()
