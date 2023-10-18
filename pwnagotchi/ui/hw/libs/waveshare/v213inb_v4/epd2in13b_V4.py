# *****************************************************************************
# * | File        :	  epd2in13b_V4.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2022-04-21
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
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

import logging
from . import epdconfig

# Display resolution
EPD_WIDTH = 122
EPD_HEIGHT = 250

logger = logging.getLogger(__name__)


class EPD:
    def __init__(self):
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin = epdconfig.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    # hardware reset
    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(20)
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(2)
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(20)

    # send 1 byte command
    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, 0)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, 1)

    # send 1 byte data
    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, 1)

    # send a lot of data
    def send_data2(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte2(data)
        epdconfig.digital_write(self.cs_pin, 1)

    # judge e-Paper whether is busy
    def busy(self):
        logger.debug("e-Paper busy")
        while (epdconfig.digital_read(self.busy_pin) != 0):
            epdconfig.delay_ms(10)
        logger.debug("e-Paper busy release")

    # set the display window
    def set_windows(self, xstart, ystart, xend, yend):
        self.send_command(0x44)  # SET_RAM_X_ADDRESS_START_END_POSITION
        self.send_data((xstart >> 3) & 0xff)
        self.send_data((xend >> 3) & 0xff)

        self.send_command(0x45)  # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(ystart & 0xff)
        self.send_data((ystart >> 8) & 0xff)
        self.send_data(yend & 0xff)
        self.send_data((yend >> 8) & 0xff)

    # set the display cursor(origin)
    def set_cursor(self, xstart, ystart):
        self.send_command(0x4E)  # SET_RAM_X_ADDRESS_COUNTER
        self.send_data(xstart & 0xff)

        self.send_command(0x4F)  # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(ystart & 0xff)
        self.send_data((ystart >> 8) & 0xff)

    # initialize
    def init(self):
        if (epdconfig.module_init() != 0):
            return -1

        self.reset()

        self.busy()
        self.send_command(0x12)  # SWRESET
        self.busy()

        self.send_command(0x01)  # Driver output control
        self.send_data(0xf9)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x11)  # data entry mode
        self.send_data(0x03)

        self.set_windows(0, 0, self.width - 1, self.height - 1)
        self.set_cursor(0, 0)

        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x05)

        self.send_command(0x18)  # Read built-in temperature sensor
        self.send_data(0x80)

        self.send_command(0x21)  # Display update control
        self.send_data(0x80)
        self.send_data(0x80)

        self.busy()

        return 0

    # turn on display
    def ondisplay(self):
        self.send_command(0x20)
        self.busy()

    # image converted to bytearray
    def getbuffer(self, image):
        img = image
        imwidth, imheight = img.size
        if (imwidth == self.width and imheight == self.height):
            img = img.convert('1')
        elif (imwidth == self.height and imheight == self.width):
            # image has correct dimensions, but needs to be rotated
            img = img.rotate(90, expand=True).convert('1')
        else:
            logger.warning("Wrong image dimensions: must be " +
                           str(self.width) + "x" + str(self.height))
            # return a blank buffer
            return [0x00] * (int(self.width/8) * self.height)

        buf = bytearray(img.tobytes('raw'))
        return buf

    # display image
    def display(self, imageblack, imagered):
        self.send_command(0x24)
        self.send_data2(imageblack)

        self.send_command(0x26)
        self.send_data2(imagered)

        self.ondisplay()

    # display white image
    def clear(self):
        if self.width % 8 == 0:
            linewidth = int(self.width/8)
        else:
            linewidth = int(self.width/8) + 1

        buf = [0xff] * (int(linewidth * self.height))

        self.send_command(0x24)
        self.send_data2(buf)

        self.send_command(0x26)
        self.send_data2(buf)

        self.ondisplay()

    # Compatible with older version functions
    def Clear(self):
        self.clear()

    # sleep
    def sleep(self):
        self.send_command(0x10)  # DEEP_SLEEP
        self.send_data(0x01)  # check code

        epdconfig.delay_ms(2000)
        epdconfig.module_exit()
### END OF FILE ###
