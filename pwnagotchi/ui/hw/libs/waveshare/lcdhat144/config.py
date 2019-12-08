# /*****************************************************************************
# * | File        :   config.py
# * | Author      :
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2019-12-06
# * | Info        :
# ******************************************************************************/
Device_SPI = 1
Device_I2C = 0
Device = Device_SPI
#spi = spidev.SpiDev(0, 0)

##
 #  @filename   :   DEV_Config.py
 #  @brief      :   LCD hardware interface implements (GPIO, SPI)
 #  @author     :   Yehui from Waveshare
 #
 #  Copyright (C) Waveshare     July 10 2017
 #
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
 
import spidev
import RPi.GPIO as GPIO
import time

# Pin definition
LCD_RST_PIN         = 27
LCD_DC_PIN          = 25
LCD_CS_PIN          = 8
LCD_BL_PIN          = 24

# SPI device, bus = 0, device = 0
SPI = spidev.SpiDev(0, 0)

def epd_digital_write(pin, value):
    GPIO.output(pin, value)

def Driver_Delay_ms(xms):
    time.sleep(xms / 1000.0)

def SPI_Write_Byte(data):
    SPI.writebytes(data)

def GPIO_Init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LCD_RST_PIN, GPIO.OUT)
    GPIO.setup(LCD_DC_PIN, GPIO.OUT)
    GPIO.setup(LCD_CS_PIN, GPIO.OUT)
    GPIO.setup(LCD_BL_PIN, GPIO.OUT)
    SPI.max_speed_hz = 9000000
    SPI.mode = 0b00
    return 0;
### END OF FILE ###
