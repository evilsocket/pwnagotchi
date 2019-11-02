# *****************************************************************************
# * | File        :	  epd2in13bc.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V4.0
# * | Date        :   2019-06-20
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from . import epdconfig
import RPi.GPIO as GPIO
# import numpy as np

# Display resolution
EPD_WIDTH       = 104
EPD_HEIGHT      = 212

class EPD:
    def __init__(self):
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin = epdconfig.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    # Hardware reset
    def reset(self):
        epdconfig.digital_write(self.reset_pin, GPIO.HIGH)
        epdconfig.delay_ms(200)
        epdconfig.digital_write(self.reset_pin, GPIO.LOW)         # module reset
        epdconfig.delay_ms(200)
        epdconfig.digital_write(self.reset_pin, GPIO.HIGH)
        epdconfig.delay_ms(200)

    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, GPIO.LOW)
        epdconfig.digital_write(self.cs_pin, GPIO.LOW)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, GPIO.HIGH)

    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, GPIO.HIGH)
        epdconfig.digital_write(self.cs_pin, GPIO.LOW)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, GPIO.HIGH)

    def ReadBusy(self):
        epdconfig.delay_ms(20)
        while(epdconfig.digital_read(self.busy_pin) == 0):      # 0: idle, 1: busy
            epdconfig.delay_ms(100)

    def init(self):
        if (epdconfig.module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()

        self.send_command(0x06) # BOOSTER_SOFT_START
        self.send_data(0x17)
        self.send_data(0x17)
        self.send_data(0x17)

        self.send_command(0x04) # POWER_ON
        self.ReadBusy()

        self.send_command(0x00) # PANEL_SETTING
        self.send_data(0x8F)

        self.send_command(0x50) # VCOM_AND_DATA_INTERVAL_SETTING
        self.send_data(0xF0)

        self.send_command(0x61) # RESOLUTION_SETTING
        self.send_data(self.width & 0xff)
        self.send_data(self.height >> 8)
        self.send_data(self.height & 0xff)
        return 0

    def getbuffer(self, image):
        buf = [0xFF] * (int(self.width/8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        if(imwidth == self.width and imheight == self.height):
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[int((x + y * self.width) / 8)] &= ~(0x80 >> (x % 8))
        elif(imwidth == self.height and imheight == self.width):
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[int((newx + newy*self.width) / 8)] &= ~(0x80 >> (y % 8))
        return buf

    def displayBlack(self, imageblack):
        self.send_command(0x10)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(imageblack[i])
        self.send_command(0x92)

        self.send_command(0x12) # REFRESH
        self.ReadBusy()

    def display(self, imageblack, imagecolor):
        self.send_command(0x10)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(imageblack[i])
        self.send_command(0x92)

        self.send_command(0x13)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(imagecolor[i])
        self.send_command(0x92)

        self.send_command(0x12) # REFRESH
        self.ReadBusy()

    def Clear(self):
        self.send_command(0x10)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)
        self.send_command(0x92)

        self.send_command(0x13)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)
        self.send_command(0x92)

        self.send_command(0x12) # REFRESH
        self.ReadBusy()

    def sleep(self):
        self.send_command(0x02) # POWER_OFF
        self.ReadBusy()
        self.send_command(0x07) # DEEP_SLEEP
        self.send_data(0xA5) # check code

#        epdconfig.module_exit()
### END OF FILE ###

