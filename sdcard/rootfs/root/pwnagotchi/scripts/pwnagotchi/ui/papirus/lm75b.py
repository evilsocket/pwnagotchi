# Minimal support for LM75b temperature sensor on the Papirus HAT / Papirus Zero
# This module allows you to read the temperature.
# The OS-output (Over-temperature Shutdown) connected to GPIO xx (pin 11) is not supported
# by this module
#

from __future__ import (print_function, division)

import smbus

LM75B_ADDRESS             = 0x48

LM75B_TEMP_REGISTER       = 0
LM75B_CONF_REGISTER       = 1
LM75B_THYST_REGISTER      = 2
LM75B_TOS_REGISTER        = 3

LM75B_CONF_NORMAL         = 0

class LM75B(object):
    def __init__(self, address=LM75B_ADDRESS, busnum=1):
        self._address = address
        self._bus = smbus.SMBus(busnum)
        self._bus.write_byte_data(self._address, LM75B_CONF_REGISTER, LM75B_CONF_NORMAL)

    def getTempCFloat(self):
        """Return temperature in degrees Celsius as float"""
        raw = self._bus.read_word_data(self._address, LM75B_TEMP_REGISTER) & 0xFFFF
        raw = ((raw << 8) & 0xFF00) + (raw >> 8)
        return (raw / 32.0) / 8.0

    def getTempFFloat(self):
        """Return temperature in degrees Fahrenheit as float"""
        return (self.getTempCFloat() * (9.0 / 5.0)) + 32.0

    def getTempC(self):
        """Return temperature in degrees Celsius as integer, so it can be
           used to write to /dev/epd/temperature"""
        raw = self._bus.read_word_data(self._address, LM75B_TEMP_REGISTER) & 0xFFFF
        raw = ((raw << 8) & 0xFF00) + (raw >> 8)
        return (raw + 128) // 256 # round to nearest integer

if __name__ == "__main__":
    sens = LM75B()
    print(sens.getTempC(), sens.getTempFFloat())

