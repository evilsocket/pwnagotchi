# Waveshare 1.44inch LCD HAT
# https://www.waveshare.com/1.44inch-lcd-hat.htm
# https://www.waveshare.com/wiki/1.44inch_LCD_HAT
# Driver: ST7735S
# Interface: SPI
# Display color: RGB, 65K color
# Resolution: 128x128
# Backlight: LED
# Operating voltage: 3.3V

from . import config
from . import LCD_1in44
from PIL import ImageOps

class EPD(object):
    def __init__(self):
        self.width = 128
        self.height = 128
        self.LCD = LCD_1in44.LCD()
        self.LCD.Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
        self.LCD.LCD_Init(self.LCD.Lcd_ScanDir)

    def init(self):
        pass

    def clear(self):
        #self.LCD.LCD_Clear()
        pass

    def display(self, image):
        rgb_im = ImageOps.colorize(image.convert("L"), black ="green", white ="black")
        self.LCD.LCD_ShowImage(rgb_im, 0, 0)
