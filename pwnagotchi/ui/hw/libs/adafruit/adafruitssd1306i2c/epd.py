from . import SSD1306

RST = 24

disp = SSD1306.SSD1306_128_64(rst=RST, i2c_bus=1, i2c_address=0x3C)

class EPD(object):

    def __init__(self, rst=RST, i2c_bus=None, i2c_address=0x3c):
        self.width = 128
        self.height = 64
        if i2c_bus is None:
            self.i2c_bus = 1
        else:
            self.i2c_bus = i2c_bus
        self.i2c_address = i2c_address
        self.disp = disp

    def init(self):
        self.disp.begin()

    def Clear(self):
        self.disp.clear()
        self.disp.display()

    def display(self, image):
        self.disp.image(image)
        self.disp.display()