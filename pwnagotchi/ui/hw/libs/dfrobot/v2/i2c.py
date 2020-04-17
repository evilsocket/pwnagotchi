# -*- coding:utf-8 -*-

'''
change i2c frequency on raspberry:
  1. edit /etc/modprobe.d
  2. add line: 
    options i2c_bcm2708 baudrate=400000
'''

import smbus

class I2C:

  def __init__(self, port):
    self._bus = smbus.SMBus(port)

  def writeBytes(self, addr, reg, buf):
    self._bus.write_block_data(addr, reg, buf)
  
  def readBytes(self, addr, reg, length):
    return self._bus.read_block_data(addr, reg, length)
