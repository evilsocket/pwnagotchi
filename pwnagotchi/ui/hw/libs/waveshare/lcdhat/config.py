# /*****************************************************************************
# * | File        :   config.py
# * | Author      :   Guillaume Giraudon
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2019-10-18
# * | Info        :
# ******************************************************************************/

import RPi.GPIO as GPIO
import time
from smbus import SMBus
import spidev

import ctypes
# import spidev

# Pin definition
RST_PIN         = 27
DC_PIN          = 25
BL_PIN          = 24

Device_SPI = 1
Device_I2C = 0

Device = Device_SPI
spi = spidev.SpiDev(0, 0)

def digital_write(pin, value):
    GPIO.output(pin, value)

def digital_read(pin):
    return GPIO.input(BUSY_PIN)

def delay_ms(delaytime):
    time.sleep(delaytime / 1000.0)

def spi_writebyte(data):
    # SPI.writebytes(data)
    spi.writebytes([data[0]])

def i2c_writebyte(reg, value):
    bus.write_byte_data(address, reg, value)

    # time.sleep(0.01)
def module_init():
    # print("module_init")

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(RST_PIN, GPIO.OUT)
    GPIO.setup(DC_PIN, GPIO.OUT)


    # SPI.max_speed_hz = 2000000
    # SPI.mode = 0b00
    # i2c_writebyte(0xff,0xff)
    # spi.SYSFS_software_spi_begin()
    # spi.SYSFS_software_spi_setDataMode(0);
    # spi.SYSFS_software_spi_setClockDivider(1);
    #spi.max_speed_hz = 2000000
    #spi.mode = 0b00

    GPIO.output(BL_PIN, 1)
    GPIO.output(DC_PIN, 0)
    return 0

def module_exit():
    spi.SYSFS_software_spi_end()
    GPIO.output(RST_PIN, 0)
    GPIO.output(DC_PIN, 0)



### END OF FILE ###
