"""
Based on UPS Lite v1.1 from https://github.com/xenDE

funtions for get UPS status - needs enable "i2c" in raspi-config

https://github.com/linshuqin329/UPS-Lite

For Raspberry Pi Zero Ups Power Expansion Board with Integrated Serial Port S3U4
https://www.ebay.de/itm/For-Raspberry-Pi-Zero-Ups-Power-Expansion-Board-with-Integrated-Serial-Port-S3U4/323873804310
https://www.aliexpress.com/item/32888533624.html
"""

import os
import struct
import logging
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
from pwnagotchi.ui import fonts
from pwnagotchi.plugins import loaded

# Meta-Informations
__author__ = 'evilsocket@gmail.com'
__version__ = '1.0.0'
__name__ = 'ups_lite'
__license__ = 'GPL3'
__description__ = 'A plugin that will add a voltage indicator for the UPS Lite v1.1'

# Variables
OPTIONS = dict()
PLUGIN = loaded[os.path.basename(__file__).replace(".py","")]


# TODO: add enable switch in config.yml an cleanup all to the best place
class UPS:
    def __init__(self):
        # only import when the module is loaded and enabled
        import smbus
        # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        self._bus = smbus.SMBus(1)

    def voltage(self):
        try:
            address = 0x36
            read = self._bus.read_word_data(address, 2)
            swapped = struct.unpack("<H", struct.pack(">H", read))[0]
            return swapped * 1.25 / 1000 / 16
        except Exception as smbus_err:
            logging.error(smbus_err)
            return 0.0

    def capacity(self):
        try:
            address = 0x36
            read = self._bus.read_word_data(address, 4)
            swapped = struct.unpack("<H", struct.pack(">H", read))[0]
            return swapped / 256
        except Exception as smbus_err:
            logging.error(smbus_err)
            return 0.0


def on_loaded():
    PLUGIN.ups = UPS()


def on_ui_setup(ui):
    ui.add_element('ups', LabeledValue(color=BLACK, label='UPS', value='0%/0V', position=(ui.width() / 2 - 25, 0),
                                       label_font=fonts.Bold, text_font=fonts.Medium))


def on_ui_update(ui):
    ui.set('ups', "%4.2fV/%2i%%" % (PLUGIN.ups.voltage(), PLUGIN.ups.capacity()))
