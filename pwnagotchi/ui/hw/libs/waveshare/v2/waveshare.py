# //*****************************************************************************
# * | File        :	  epd2in13.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * |	This version:   V3.0
# * | Date        :   2018-11-01
# * | Info        :   python2 demo
# * 1.Remove:
#   digital_write(self, pin, value)
#   digital_read(self, pin)
#   delay_ms(self, delaytime)
#   set_lut(self, lut)
#   self.lut = self.lut_full_update
# * 2.Change:
#   display_frame -> TurnOnDisplay
#   set_memory_area -> SetWindow
#   set_memory_pointer -> SetCursor
# * 3.How to use
#   epd = epd2in13.EPD()
#   epd.init(epd.lut_full_update)
#   image = Image.new('1', (epd2in13.EPD_WIDTH, epd2in13.EPD_HEIGHT), 255)
#   ...
#   drawing ......
#   ...
#   epd.display(getbuffer(image))
# ******************************************************************************//
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and//or sell
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

import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image

# Pin definition
RST_PIN = 17
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 24

# SPI device, bus = 0, device = 0
SPI = spidev.SpiDev(0, 0)


def digital_write(pin, value):
    GPIO.output(pin, value)


def digital_read(pin):
    return GPIO.input(BUSY_PIN)


def delay_ms(delaytime):
    time.sleep(delaytime / 1000.0)


def spi_writebyte(data):
    SPI.writebytes(data)


def module_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(RST_PIN, GPIO.OUT)
    GPIO.setup(DC_PIN, GPIO.OUT)
    GPIO.setup(CS_PIN, GPIO.OUT)
    GPIO.setup(BUSY_PIN, GPIO.IN)
    SPI.max_speed_hz = 2000000
    SPI.mode = 0b00
    return 0;


# Display resolution
EPD_WIDTH = 122
EPD_HEIGHT = 250


class EPD:
    def __init__(self):
        self.reset_pin = RST_PIN
        self.dc_pin = DC_PIN
        self.busy_pin = BUSY_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    FULL_UPDATE = 0
    PART_UPDATE = 1
    lut_full_update = [
        0x80, 0x60, 0x40, 0x00, 0x00, 0x00, 0x00,  # LUT0: BB:     VS 0 ~7
        0x10, 0x60, 0x20, 0x00, 0x00, 0x00, 0x00,  # LUT1: BW:     VS 0 ~7
        0x80, 0x60, 0x40, 0x00, 0x00, 0x00, 0x00,  # LUT2: WB:     VS 0 ~7
        0x10, 0x60, 0x20, 0x00, 0x00, 0x00, 0x00,  # LUT3: WW:     VS 0 ~7
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # LUT4: VCOM:   VS 0 ~7

        0x03, 0x03, 0x00, 0x00, 0x02,  # TP0 A~D RP0
        0x09, 0x09, 0x00, 0x00, 0x02,  # TP1 A~D RP1
        0x03, 0x03, 0x00, 0x00, 0x02,  # TP2 A~D RP2
        0x00, 0x00, 0x00, 0x00, 0x00,  # TP3 A~D RP3
        0x00, 0x00, 0x00, 0x00, 0x00,  # TP4 A~D RP4
        0x00, 0x00, 0x00, 0x00, 0x00,  # TP5 A~D RP5
        0x00, 0x00, 0x00, 0x00, 0x00,  # TP6 A~D RP6

        0x15, 0x41, 0xA8, 0x32, 0x30, 0x0A,
    ]

    lut_partial_update = [  # 20 bytes
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # LUT0: BB:     VS 0 ~7
        0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # LUT1: BW:     VS 0 ~7
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # LUT2: WB:     VS 0 ~7
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # LUT3: WW:     VS 0 ~7
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # LUT4: VCOM:   VS 0 ~7

        0x0A, 0x00, 0x00, 0x00, 0x00,  # TP0 A~D RP0
        0x00, 0x00, 0x00, 0x00, 0x00,  # TP1 A~D RP1
        0x00, 0x00, 0x00, 0x00, 0x00,  # TP2 A~D RP2
        0x00, 0x00, 0x00, 0x00, 0x00,  # TP3 A~D RP3
        0x00, 0x00, 0x00, 0x00, 0x00,  # TP4 A~D RP4
        0x00, 0x00, 0x00, 0x00, 0x00,  # TP5 A~D RP5
        0x00, 0x00, 0x00, 0x00, 0x00,  # TP6 A~D RP6

        0x15, 0x41, 0xA8, 0x32, 0x30, 0x0A,
    ]

    # Hardware reset
    def reset(self):
        digital_write(self.reset_pin, GPIO.HIGH)
        delay_ms(200)
        digital_write(self.reset_pin, GPIO.LOW)  # module reset
        delay_ms(200)
        digital_write(self.reset_pin, GPIO.HIGH)
        delay_ms(200)

    def send_command(self, command):
        digital_write(self.dc_pin, GPIO.LOW)
        spi_writebyte([command])

    def send_data(self, data):
        digital_write(self.dc_pin, GPIO.HIGH)
        spi_writebyte([data])

    def wait_until_idle(self):
        while (digital_read(self.busy_pin) == 1):  # 0: idle, 1: busy
            delay_ms(100)

    def TurnOnDisplay(self):
        self.send_command(0x22)
        self.send_data(0xC7)
        self.send_command(0x20)
        self.wait_until_idle()

    def init(self, update):
        if (module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()
        if (update == self.FULL_UPDATE):
            self.wait_until_idle()
            self.send_command(0x12)  # soft reset
            self.wait_until_idle()

            self.send_command(0x74)  # set analog block control
            self.send_data(0x54)
            self.send_command(0x7E)  # set digital block control
            self.send_data(0x3B)

            self.send_command(0x01)  # Driver output control
            self.send_data(0xF9)
            self.send_data(0x00)
            self.send_data(0x00)

            self.send_command(0x11)  # data entry mode
            self.send_data(0x01)

            self.send_command(0x44)  # set Ram-X address start//end position
            self.send_data(0x00)
            self.send_data(0x0F)  # 0x0C-->(15+1)*8=128

            self.send_command(0x45)  # set Ram-Y address start//end position
            self.send_data(0xF9)  # 0xF9-->(249+1)=250
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)

            self.send_command(0x3C)  # BorderWavefrom
            self.send_data(0x03)

            self.send_command(0x2C)  # VCOM Voltage
            self.send_data(0x55)  #

            self.send_command(0x03)
            self.send_data(self.lut_full_update[70])

            self.send_command(0x04)  #
            self.send_data(self.lut_full_update[71])
            self.send_data(self.lut_full_update[72])
            self.send_data(self.lut_full_update[73])

            self.send_command(0x3A)  # Dummy Line
            self.send_data(self.lut_full_update[74])
            self.send_command(0x3B)  # Gate time
            self.send_data(self.lut_full_update[75])

            self.send_command(0x32)
            for count in range(70):
                self.send_data(self.lut_full_update[count])

            self.send_command(0x4E)  # set RAM x address count to 0
            self.send_data(0x00)
            self.send_command(0x4F)  # set RAM y address count to 0X127
            self.send_data(0xF9)
            self.send_data(0x00)
            self.wait_until_idle()
        else:
            self.send_command(0x2C)  # VCOM Voltage
            self.send_data(0x26)

            self.wait_until_idle()

            self.send_command(0x32)
            for count in range(70):
                self.send_data(self.lut_partial_update[count])

            self.send_command(0x37)
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x40)
            self.send_data(0x00)
            self.send_data(0x00)

            self.send_command(0x22)
            self.send_data(0xC0)
            self.send_command(0x20)
            self.wait_until_idle()

            self.send_command(0x3C)  # BorderWavefrom
            self.send_data(0x01)
        return 0

    def getbuffer(self, image):
        if self.width % 8 == 0:
            linewidth = self.width // 8
        else:
            linewidth = self.width // 8 + 1

        buf = [0xFF] * (linewidth * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()

        if (imwidth == self.width and imheight == self.height):
            # print("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    if pixels[x, y] == 0:
                        x = imwidth - x
                        buf[x // 8 + y * linewidth] &= ~(0x80 >> (x % 8))
        elif (imwidth == self.height and imheight == self.width):
            # print("Horizontal")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        newy = imwidth - newy - 1
                        buf[newx // 8 + newy * linewidth] &= ~(0x80 >> (y % 8))
        return buf

    def display(self, image):
        if self.width % 8 == 0:
            linewidth = self.width // 8
        else:
            linewidth = self.width // 8 + 1

        self.send_command(0x24)
        for j in range(0, self.height):
            for i in range(0, linewidth):
                self.send_data(image[i + j * linewidth])
        self.TurnOnDisplay()

    def displayPartial(self, image):
        if self.width % 8 == 0:
            linewidth = self.width // 8
        else:
            linewidth = self.width // 8 + 1

        self.send_command(0x24)
        for j in range(0, self.height):
            for i in range(0, linewidth):
                self.send_data(image[i + j * linewidth])
        self.send_command(0x26)
        for j in range(0, self.height):
            for i in range(0, linewidth):
                self.send_data(~image[i + j * linewidth])
        self.TurnOnDisplay()

    def Clear(self, color):
        if self.width % 8 == 0:
            linewidth = self.width // 8
        else:
            linewidth = self.width // 8 + 1
        # print(linewidth)

        self.send_command(0x24)
        for j in range(0, self.height):
            for i in range(0, linewidth):
                self.send_data(color)
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x22)  # POWER OFF
        self.send_data(0xC3)
        self.send_command(0x20)

        self.send_command(0x10)  # enter deep sleep
        self.send_data(0x01)
        delay_ms(100)

    ### END OF FILE ###