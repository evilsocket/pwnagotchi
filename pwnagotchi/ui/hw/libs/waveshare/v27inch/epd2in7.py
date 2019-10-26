# *****************************************************************************
# * | File        :	  epd2in7.py
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
EPD_WIDTH       = 176
EPD_HEIGHT      = 264

GRAY1  = 0xff #white
GRAY2  = 0xC0
GRAY3  = 0x80 #gray
GRAY4  = 0x00 #Blackest
class EPD:
    def __init__(self):
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin = epdconfig.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.GRAY1  = GRAY1 #white
        self.GRAY2  = GRAY2
        self.GRAY3  = GRAY3 #gray
        self.GRAY4  = GRAY4 #Blackest

    lut_vcom_dc = [0x00, 0x00,
        0x00, 0x08, 0x00, 0x00, 0x00, 0x02,
        0x60, 0x28, 0x28, 0x00, 0x00, 0x01,
        0x00, 0x14, 0x00, 0x00, 0x00, 0x01,
        0x00, 0x12, 0x12, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    lut_ww = [
        0x40, 0x08, 0x00, 0x00, 0x00, 0x02,
        0x90, 0x28, 0x28, 0x00, 0x00, 0x01,
        0x40, 0x14, 0x00, 0x00, 0x00, 0x01,
        0xA0, 0x12, 0x12, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]
    lut_bw = [
        0x40, 0x08, 0x00, 0x00, 0x00, 0x02,
        0x90, 0x28, 0x28, 0x00, 0x00, 0x01,
        0x40, 0x14, 0x00, 0x00, 0x00, 0x01,
        0xA0, 0x12, 0x12, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]
    lut_bb = [
        0x80, 0x08, 0x00, 0x00, 0x00, 0x02,
        0x90, 0x28, 0x28, 0x00, 0x00, 0x01,
        0x80, 0x14, 0x00, 0x00, 0x00, 0x01,
        0x50, 0x12, 0x12, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]
    lut_wb = [
        0x80, 0x08, 0x00, 0x00, 0x00, 0x02,
        0x90, 0x28, 0x28, 0x00, 0x00, 0x01,
        0x80, 0x14, 0x00, 0x00, 0x00, 0x01,
        0x50, 0x12, 0x12, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]
    ###################full screen update LUT######################
    #0~3 gray
    gray_lut_vcom = [
    0x00, 0x00,
    0x00, 0x0A, 0x00, 0x00, 0x00, 0x01,
    0x60, 0x14, 0x14, 0x00, 0x00, 0x01,
    0x00, 0x14, 0x00, 0x00, 0x00, 0x01,
    0x00, 0x13, 0x0A, 0x01, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,				
    ]
    #R21
    gray_lut_ww =[
    0x40, 0x0A, 0x00, 0x00, 0x00, 0x01,
    0x90, 0x14, 0x14, 0x00, 0x00, 0x01,
    0x10, 0x14, 0x0A, 0x00, 0x00, 0x01,
    0xA0, 0x13, 0x01, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]
    #R22H	r
    gray_lut_bw =[
    0x40, 0x0A, 0x00, 0x00, 0x00, 0x01,
    0x90, 0x14, 0x14, 0x00, 0x00, 0x01,
    0x00, 0x14, 0x0A, 0x00, 0x00, 0x01,
    0x99, 0x0C, 0x01, 0x03, 0x04, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]
    #R23H	w
    gray_lut_wb =[
    0x40, 0x0A, 0x00, 0x00, 0x00, 0x01,
    0x90, 0x14, 0x14, 0x00, 0x00, 0x01,
    0x00, 0x14, 0x0A, 0x00, 0x00, 0x01,
    0x99, 0x0B, 0x04, 0x04, 0x01, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]
    #R24H	b
    gray_lut_bb =[
    0x80, 0x0A, 0x00, 0x00, 0x00, 0x01,
    0x90, 0x14, 0x14, 0x00, 0x00, 0x01,
    0x20, 0x14, 0x0A, 0x00, 0x00, 0x01,
    0x50, 0x13, 0x01, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]
    
    # Hardware reset
    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(200) 
        epdconfig.digital_write(self.reset_pin, 0)
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
        while(epdconfig.digital_read(self.busy_pin) == 0):      #  0: idle, 1: busy
            epdconfig.delay_ms(200)                
        logging.debug("e-Paper busy release")

    def set_lut(self):
        self.send_command(0x20) # vcom
        for count in range(0, 44):
            self.send_data(self.lut_vcom_dc[count])
        self.send_command(0x21) # ww --
        for count in range(0, 42):
            self.send_data(self.lut_ww[count])
        self.send_command(0x22) # bw r
        for count in range(0, 42):
            self.send_data(self.lut_bw[count])
        self.send_command(0x23) # wb w
        for count in range(0, 42):
            self.send_data(self.lut_bb[count])
        self.send_command(0x24) # bb b
        for count in range(0, 42):
            self.send_data(self.lut_wb[count])
            
    def gray_SetLut(self):
        self.send_command(0x20)
        for count in range(0, 44):        #vcom
            self.send_data(self.gray_lut_vcom[count])
            
        self.send_command(0x21)							#red not use
        for count in range(0, 42): 
            self.send_data(self.gray_lut_ww[count])

        self.send_command(0x22)							#bw r
        for count in range(0, 42): 
            self.send_data(self.gray_lut_bw[count])

        self.send_command(0x23)							#wb w
        for count in range(0, 42): 
            self.send_data(self.gray_lut_wb[count])

        self.send_command(0x24)							#bb b
        for count in range(0, 42): 
            self.send_data(self.gray_lut_bb[count])

        self.send_command(0x25)							#vcom
        for count in range(0, 42): 
            self.send_data(self.gray_lut_ww[count])
    
    def init(self):
        if (epdconfig.module_init() != 0):
            return -1
            
        # EPD hardware init start
        self.reset()
        
        self.send_command(0x01) # POWER_SETTING
        self.send_data(0x03) # VDS_EN, VDG_EN
        self.send_data(0x00) # VCOM_HV, VGHL_LV[1], VGHL_LV[0]
        self.send_data(0x2b) # VDH
        self.send_data(0x2b) # VDL
        self.send_data(0x09) # VDHR
        
        self.send_command(0x06) # BOOSTER_SOFT_START
        self.send_data(0x07)
        self.send_data(0x07)
        self.send_data(0x17)
        
        # Power optimization
        self.send_command(0xF8)
        self.send_data(0x60)
        self.send_data(0xA5)
        
        # Power optimization
        self.send_command(0xF8)
        self.send_data(0x89)
        self.send_data(0xA5)
        
        # Power optimization
        self.send_command(0xF8)
        self.send_data(0x90)
        self.send_data(0x00)
        
        # Power optimization
        self.send_command(0xF8)
        self.send_data(0x93)
        self.send_data(0x2A)
        
        # Power optimization
        self.send_command(0xF8)
        self.send_data(0xA0)
        self.send_data(0xA5)
        
        # Power optimization
        self.send_command(0xF8)
        self.send_data(0xA1)
        self.send_data(0x00)
        
        # Power optimization
        self.send_command(0xF8)
        self.send_data(0x73)
        self.send_data(0x41)
        
        self.send_command(0x16) # PARTIAL_DISPLAY_REFRESH
        self.send_data(0x00)
        self.send_command(0x04) # POWER_ON
        self.ReadBusy()

        self.send_command(0x00) # PANEL_SETTING
        self.send_data(0xAF) # KW-BF   KWR-AF    BWROTP 0f
        
        self.send_command(0x30) # PLL_CONTROL
        self.send_data(0x3A) # 3A 100HZ   29 150Hz 39 200HZ    31 171HZ
        
        self.send_command(0x82) # VCM_DC_SETTING_REGISTER
        self.send_data(0x12)
        self.set_lut()
        return 0

    def Init_4Gray(self):
        if (epdconfig.module_init() != 0):
            return -1
        self.reset()
        
        self.send_command(0x01)			#POWER SETTING
        self.send_data (0x03)
        self.send_data (0x00)    
        self.send_data (0x2b)															 
        self.send_data (0x2b)		


        self.send_command(0x06)         #booster soft start
        self.send_data (0x07)		#A
        self.send_data (0x07)		#B
        self.send_data (0x17)		#C 

        self.send_command(0xF8)         #boost??
        self.send_data (0x60)
        self.send_data (0xA5)

        self.send_command(0xF8)         #boost??
        self.send_data (0x89)
        self.send_data (0xA5)

        self.send_command(0xF8)         #boost??
        self.send_data (0x90)
        self.send_data (0x00)

        self.send_command(0xF8)         #boost??
        self.send_data (0x93)
        self.send_data (0x2A)

        self.send_command(0xF8)         #boost??
        self.send_data (0xa0)
        self.send_data (0xa5)

        self.send_command(0xF8)         #boost??
        self.send_data (0xa1)
        self.send_data (0x00)

        self.send_command(0xF8)         #boost??
        self.send_data (0x73)
        self.send_data (0x41)

        self.send_command(0x16)
        self.send_data(0x00)	

        self.send_command(0x04)
        self.ReadBusy()

        self.send_command(0x00)			#panel setting
        self.send_data(0xbf)		#KW-BF   KWR-AF	BWROTP 0f

        self.send_command(0x30)			#PLL setting
        self.send_data (0x90)      	#100hz 

        self.send_command(0x61)			#resolution setting
        self.send_data (0x00)		#176
        self.send_data (0xb0)     	 
        self.send_data (0x01)		#264
        self.send_data (0x08)

        self.send_command(0x82)			#vcom_DC setting
        self.send_data (0x12)

        self.send_command(0X50)			#VCOM AND DATA INTERVAL SETTING			
        self.send_data(0x97)

    def getbuffer(self, image):
        # logging.debug("bufsiz = ",int(self.width/8) * self.height)
        buf = [0xFF] * (int(self.width/8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        # logging.debug("imwidth = %d, imheight = %d",imwidth,imheight)
        if(imwidth == self.width and imheight == self.height):
            logging.debug("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[int((x + y * self.width) / 8)] &= ~(0x80 >> (x % 8))
        elif(imwidth == self.height and imheight == self.width):
            logging.debug("Horizontal")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[int((newx + newy*self.width) / 8)] &= ~(0x80 >> (y % 8))
        return buf
    
    def getbuffer_4Gray(self, image):
        # logging.debug("bufsiz = ",int(self.width/8) * self.height)
        buf = [0xFF] * (int(self.width / 4) * self.height)
        image_monocolor = image.convert('L')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        i=0
        # logging.debug("imwidth = %d, imheight = %d",imwidth,imheight)
        if(imwidth == self.width and imheight == self.height):
            logging.debug("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if(pixels[x, y] == 0xC0):
                        pixels[x, y] = 0x80
                    elif (pixels[x, y] == 0x80):
                        pixels[x, y] = 0x40
                    i= i+1
                    if(i%4 == 0):
                        buf[int((x + (y * self.width))/4)] = ((pixels[x-3, y]&0xc0) | (pixels[x-2, y]&0xc0)>>2 | (pixels[x-1, y]&0xc0)>>4 | (pixels[x, y]&0xc0)>>6)
                        
        elif(imwidth == self.height and imheight == self.width):
            logging.debug("Horizontal")
            for x in range(imwidth):
                for y in range(imheight):
                    newx = y
                    newy = x
                    if(pixels[x, y] == 0xC0):
                        pixels[x, y] = 0x80
                    elif (pixels[x, y] == 0x80):
                        pixels[x, y] = 0x40
                    i= i+1
                    if(i%4 == 0):
                        buf[int((newx + (newy * self.width))/4)] = ((pixels[x, y-3]&0xc0) | (pixels[x, y-2]&0xc0)>>2 | (pixels[x, y-1]&0xc0)>>4 | (pixels[x, y]&0xc0)>>6) 
        return buf
    
    def display(self, image):
        self.send_command(0x10)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)
        self.send_command(0x13)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(image[i])
        self.send_command(0x12) 
        self.ReadBusy()

    def display_4Gray(self, image):
        self.send_command(0x10)
        for i in range(0, 5808):                     #5808*4  46464
            temp3=0
            for j in range(0, 2):
                temp1 = image[i*2+j]
                for k in range(0, 2):
                    temp2 = temp1&0xC0 
                    if(temp2 == 0xC0):
                        temp3 |= 0x01#white
                    elif(temp2 == 0x00):
                        temp3 |= 0x00  #black
                    elif(temp2 == 0x80): 
                        temp3 |= 0x01  #gray1
                    else: #0x40
                        temp3 |= 0x00 #gray2
                    temp3 <<= 1	
                    
                    temp1 <<= 2
                    temp2 = temp1&0xC0 
                    if(temp2 == 0xC0):  #white
                        temp3 |= 0x01
                    elif(temp2 == 0x00): #black
                        temp3 |= 0x00
                    elif(temp2 == 0x80):
                        temp3 |= 0x01 #gray1
                    else :   #0x40
                            temp3 |= 0x00	#gray2	
                    if(j!=1 or k!=1):				
                        temp3 <<= 1
                    temp1 <<= 2
            self.send_data(temp3)
            
        self.send_command(0x13)	       
        for i in range(0, 5808):                #5808*4  46464
            temp3=0
            for j in range(0, 2):
                temp1 = image[i*2+j]
                for k in range(0, 2):
                    temp2 = temp1&0xC0 
                    if(temp2 == 0xC0):
                        temp3 |= 0x01#white
                    elif(temp2 == 0x00):
                        temp3 |= 0x00  #black
                    elif(temp2 == 0x80):
                        temp3 |= 0x00  #gray1
                    else: #0x40
                        temp3 |= 0x01 #gray2
                    temp3 <<= 1	
                    
                    temp1 <<= 2
                    temp2 = temp1&0xC0 
                    if(temp2 == 0xC0):  #white
                        temp3 |= 0x01
                    elif(temp2 == 0x00): #black
                        temp3 |= 0x00
                    elif(temp2 == 0x80):
                        temp3 |= 0x00 #gray1
                    else:    #0x40
                            temp3 |= 0x01	#gray2
                    if(j!=1 or k!=1):					
                        temp3 <<= 1
                    temp1 <<= 2
            self.send_data(temp3)
        
        self.gray_SetLut()
        self.send_command(0x12)
        epdconfig.delay_ms(200)
        self.ReadBusy()
        # pass
        
    def Clear(self, color):
        self.send_command(0x10)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)
        self.send_command(0x13)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)
        self.send_command(0x12) 
        self.ReadBusy()

    def sleep(self):
        self.send_command(0X50)
        self.send_data(0xf7)
        self.send_command(0X02)
        self.send_command(0X07)
        self.send_data(0xA5)
        
        epdconfig.module_exit()
### END OF FILE ###

