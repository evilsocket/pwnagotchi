from . import config
import RPi.GPIO as GPIO
import time

Device_SPI = config.Device_SPI
Device_I2C = config.Device_I2C

LCD_WIDTH   = 128 #LCD width
LCD_HEIGHT  = 64  #LCD height

class SH1106(object):
    def __init__(self):
        self.width = LCD_WIDTH
        self.height = LCD_HEIGHT
        #Initialize DC RST pin
        self._dc = config.DC_PIN
        self._rst = config.RST_PIN
        self._bl = config.BL_PIN
        self.Device = config.Device


    """    Write register address and data     """
    def command(self, cmd):
        if(self.Device == Device_SPI):
            GPIO.output(self._dc, GPIO.LOW)
            config.spi_writebyte([cmd])
        else:
            config.i2c_writebyte(0x00, cmd)

    # def data(self, val):
        # GPIO.output(self._dc, GPIO.HIGH)
        # config.spi_writebyte([val])

    def Init(self):
        if (config.module_init() != 0):
            return -1
        """Initialize display"""
        self.reset()
        self.command(0xAE);#--turn off oled panel
        self.command(0x02);#---set low column address
        self.command(0x10);#---set high column address
        self.command(0x40);#--set start line address  Set Mapping RAM Display Start Line (0x00~0x3F)
        self.command(0x81);#--set contrast control register
        self.command(0xA0);#--Set SEG/Column Mapping
        self.command(0xC0);#Set COM/Row Scan Direction
        self.command(0xA6);#--set normal display
        self.command(0xA8);#--set multiplex ratio(1 to 64)
        self.command(0x3F);#--1/64 duty
        self.command(0xD3);#-set display offset    Shift Mapping RAM Counter (0x00~0x3F)
        self.command(0x00);#-not offset
        self.command(0xd5);#--set display clock divide ratio/oscillator frequency
        self.command(0x80);#--set divide ratio, Set Clock as 100 Frames/Sec
        self.command(0xD9);#--set pre-charge period
        self.command(0xF1);#Set Pre-Charge as 15 Clocks & Discharge as 1 Clock
        self.command(0xDA);#--set com pins hardware configuration
        self.command(0x12);
        self.command(0xDB);#--set vcomh
        self.command(0x40);#Set VCOM Deselect Level
        self.command(0x20);#-Set Page Addressing Mode (0x00/0x01/0x02)
        self.command(0x02);#
        self.command(0xA4);# Disable Entire Display On (0xa4/0xa5)
        self.command(0xA6);# Disable Inverse Display On (0xa6/a7)
        time.sleep(0.1)
        self.command(0xAF);#--turn on oled panel


    def reset(self):
        """Reset the display"""
        GPIO.output(self._rst,GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self._rst,GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self._rst,GPIO.HIGH)
        time.sleep(0.1)

    def getbuffer(self, image):
        # print "bufsiz = ",(self.width/8) * self.height
        buf = [0xFF] * ((self.width//8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        # print "imwidth = %d, imheight = %d",imwidth,imheight
        if(imwidth == self.width and imheight == self.height):
            #print ("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[x + (y // 8) * self.width] &= ~(1 << (y % 8))
                        # print x,y,x + (y * self.width)/8,buf[(x + y * self.width) / 8]

        elif(imwidth == self.height and imheight == self.width):
            #print ("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[(newx + (newy // 8 )*self.width) ] &= ~(1 << (y % 8))
        return buf


    # def ShowImage(self,Image):
        # self.SetWindows()
        # GPIO.output(self._dc, GPIO.HIGH);
        # for i in range(0,self.width * self.height/8):
            # config.spi_writebyte([~Image[i]])

    def ShowImage(self, pBuf):
        for page in range(0,8):
            # set page address #
            self.command(0xB0 + page);
            # set low column address #
            self.command(0x02);
            # set high column address #
            self.command(0x10);
            # write data #
            time.sleep(0.01)
            if(self.Device == Device_SPI):
                GPIO.output(self._dc, GPIO.HIGH);
            for i in range(0,self.width):#for(int i=0;i<self.width; i++)
                if(self.Device == Device_SPI):
                    config.spi_writebyte([~pBuf[i + self.width * page]]);
                else :
                    config.i2c_writebyte(0x40, ~pBuf[i + self.width * page])





    def clear(self):
        """Clear contents of image buffer"""
        _buffer = [0xff]*(self.width * self.height//8)
        self.ShowImage(_buffer)
            #print "%d",_buffer[i:i+4096]
