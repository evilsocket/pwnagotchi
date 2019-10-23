from . import SH1106
from . import config

# Display resolution
EPD_WIDTH       = 64
EPD_HEIGHT      = 128

disp = SH1106.SH1106()

class EPD(object):

    def __init__(self):
        self.reset_pin = config.RST_PIN
        self.dc_pin = config.DC_PIN
        self.busy_pin = config.BUSY_PIN
        self.cs_pin = config.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    def init(self):
        disp.Init()

    def Clear(self):
        disp.clear()

    def display(self, image):
        disp.ShowImage(disp.getbuffer(image))
