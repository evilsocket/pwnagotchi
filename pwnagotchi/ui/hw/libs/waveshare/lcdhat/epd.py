from . import ST7789
from . import config


class EPD(object):
    def __init__(self):
        self.reset_pin = config.RST_PIN
        self.dc_pin = config.DC_PIN
        self.width = 240
        self.height = 240
        self.st7789 = ST7789.ST7789(config.spi, config.RST_PIN, config.DC_PIN, config.BL_PIN)

    def init(self):
        self.st7789.Init()

    def clear(self):
        self.st7789.clear()

    def display(self, image):
        rgb_im = image.convert('RGB')
        self.st7789.ShowImage(rgb_im, 0, 0)
