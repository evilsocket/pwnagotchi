from . import ST7789
from . import config

# Display resolution
EPD_WIDTH       = 240
EPD_HEIGHT      = 240

disp = ST7789.ST7789(config.spi,config.RST_PIN, config.DC_PIN, config.BL_PIN)

class EPD(object):

    def __init__(self):
        self.reset_pin = config.RST_PIN
        self.dc_pin = config.DC_PIN
        #self.busy_pin = config.BUSY_PIN
        #self.cs_pin = config.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    def init(self):
        disp.Init()

    def Clear(self):
        disp.clear()

    def display(self, image):
        rgb_im = image.convert('RGB')
        disp.ShowImage(rgb_im,0,0)
