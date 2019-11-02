# *****************************************************************************
# * | File        :	  epd1in54b.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V4.0
# * | Date        :   2019-06-20
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
EPD_WIDTH       = 200
EPD_HEIGHT      = 200

class EPD:
    def __init__(self):
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin = epdconfig.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    lut_vcom0 = [0x0E, 0x14, 0x01, 0x0A, 0x06, 0x04, 0x0A, 0x0A, 0x0F, 0x03, 0x03, 0x0C, 0x06, 0x0A, 0x00]
    lut_w = [0x0E, 0x14, 0x01, 0x0A, 0x46, 0x04, 0x8A, 0x4A, 0x0F, 0x83, 0x43, 0x0C, 0x86, 0x0A, 0x04]
    lut_b = [0x0E, 0x14, 0x01, 0x8A, 0x06, 0x04, 0x8A, 0x4A, 0x0F, 0x83, 0x43, 0x0C, 0x06, 0x4A, 0x04]
    lut_g1 = [0x8E, 0x94, 0x01, 0x8A, 0x06, 0x04, 0x8A, 0x4A, 0x0F, 0x83, 0x43, 0x0C, 0x06, 0x0A, 0x04]
    lut_g2 = [0x8E, 0x94, 0x01, 0x8A, 0x06, 0x04, 0x8A, 0x4A, 0x0F, 0x83, 0x43, 0x0C, 0x06, 0x0A, 0x04]
    lut_vcom1 = [0x03, 0x1D, 0x01, 0x01, 0x08, 0x23, 0x37, 0x37, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    lut_red0 = [0x83, 0x5D, 0x01, 0x81, 0x48, 0x23, 0x77, 0x77, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    lut_red1 = [0x03, 0x1D, 0x01, 0x01, 0x08, 0x23, 0x37, 0x37, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00] 
    
    # Hardware reset
    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(200) 
        epdconfig.digital_write(self.reset_pin, 0) # module reset
        epdconfig.delay_ms(10)
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(200)   

    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, 0)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, 1)
        
    def ReadBusy(self):
        logging.debug("e-Paper busy")
        while(epdconfig.digital_read(self.busy_pin) == 0):
            epdconfig.delay_ms(100)    
        logging.debug("e-Paper busy release")
      
    def set_lut_bw(self):
        self.send_command(0x20) # vcom
        for count in range(0, 15):
            self.send_data(self.lut_vcom0[count])
        self.send_command(0x21) # ww --
        for count in range(0, 15):
            self.send_data(self.lut_w[count])
        self.send_command(0x22) # bw r
        for count in range(0, 15):
            self.send_data(self.lut_b[count])
        self.send_command(0x23) # wb w
        for count in range(0, 15):
            self.send_data(self.lut_g1[count])
        self.send_command(0x24) # bb b
        for count in range(0, 15):
            self.send_data(self.lut_g2[count])

    def set_lut_red(self):
        self.send_command(0x25)
        for count in range(0, 15):
            self.send_data(self.lut_vcom1[count])
        self.send_command(0x26)
        for count in range(0, 15):
            self.send_data(self.lut_red0[count])
        self.send_command(0x27)
        for count in range(0, 15):
            self.send_data(self.lut_red1[count])
            
    def init(self):
        if (epdconfig.module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()
        
        self.send_command(0x01) # POWER_SETTING
        self.send_data(0x07)
        self.send_data(0x00)
        self.send_data(0x08)
        self.send_data(0x00)
        self.send_command(0x06) # BOOSTER_SOFT_START
        self.send_data(0x07)
        self.send_data(0x07)
        self.send_data(0x07)
        self.send_command(0x04) # POWER_ON

        self.ReadBusy()

        self.send_command(0X00) # PANEL_SETTING
        self.send_data(0xCF)
        self.send_command(0X50) # VCOM_AND_DATA_INTERVAL_SETTING
        self.send_data(0x17)
        self.send_command(0x30) # PLL_CONTROL
        self.send_data(0x39)
        self.send_command(0x61) # TCON_RESOLUTION set x and y
        self.send_data(0xC8)
        self.send_data(0x00)
        self.send_data(0xC8)
        self.send_command(0x82) # VCM_DC_SETTING_REGISTER
        self.send_data(0x0E)
        
        self.set_lut_bw()
        self.set_lut_red()
        return 0

    def getbuffer(self, image):
        buf = [0xFF] * int(self.width * self.height / 8)
        # Set buffer to value of Python Imaging Library image.
        # Image must be in mode 1.
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError('Image must be same dimensions as display \
                ({0}x{1}).' .format(self.width, self.height))

        pixels = image_monocolor.load()
        for y in range(self.height):
            for x in range(self.width):
                # Set the bits for the column of pixels at the current position.
                if pixels[x, y] == 0:
                    buf[int((x + y * self.width) / 8)] &= ~(0x80 >> (x % 8))
        return buf

    def display(self, blackimage, redimage):
        # send black data
        if (blackimage != None):
            self.send_command(0x10) # DATA_START_TRANSMISSION_1
            for i in range(0, int(self.width * self.height / 8)):
                temp = 0x00
                for bit in range(0, 4):
                    if (blackimage[i] & (0x80 >> bit) != 0):
                        temp |= 0xC0 >> (bit * 2)
                self.send_data(temp)  
                temp = 0x00
                for bit in range(4, 8):
                    if (blackimage[i] & (0x80 >> bit) != 0):
                        temp |= 0xC0 >> ((bit - 4) * 2)
                self.send_data(temp)
                
        # send red data        
        if (redimage != None):
            self.send_command(0x13) # DATA_START_TRANSMISSION_2
            for i in range(0, int(self.width * self.height / 8)):
                self.send_data(redimage[i])  

        self.send_command(0x12) # DISPLAY_REFRESH
        self.ReadBusy()

    def Clear(self):
        self.send_command(0x10) # DATA_START_TRANSMISSION_1
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)
            self.send_data(0xFF)
            
        self.send_command(0x13) # DATA_START_TRANSMISSION_2
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)

        self.send_command(0x12) # DISPLAY_REFRESH
        self.ReadBusy()

    def sleep(self):
        self.send_command(0x50) # VCOM_AND_DATA_INTERVAL_SETTING
        self.send_data(0x17)
        self.send_command(0x82) # to solve Vcom drop 
        self.send_data(0x00)        
        self.send_command(0x01) # power setting      
        self.send_data(0x02) # gate switch to external
        self.send_data(0x00)
        self.send_data(0x00) 
        self.send_data(0x00) 
        self.ReadBusy()
        
        self.send_command(0x02) # power off
        
        epdconfig.module_exit()

### END OF FILE ###

