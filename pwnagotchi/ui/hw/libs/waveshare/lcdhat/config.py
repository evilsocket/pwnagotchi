# /*****************************************************************************
# * | File        :   config.py
# * | Author      :   Guillaume Giraudon
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2019-10-18
# * | Info        :
# ******************************************************************************/
import spidev

# Pin definition
RST_PIN = 27
DC_PIN = 25
BL_PIN = 24

Device_SPI = 1
Device_I2C = 0

Device = Device_SPI
spi = spidev.SpiDev(0, 0)
