# -*- coding:utf-8 -*-

import spidev

class SPI:

  MODE_1 = 1
  MODE_2 = 2
  MODE_3 = 3
  MODE_4 = 4

  def __init__(self, bus, dev, speed = 3900000, mode = MODE_4):
    self._bus = spidev.SpiDev()
    self._bus.open(bus, dev)
    self._bus.no_cs = True
    self._bus.max_speed_hz = speed

  def transfer(self, buf):
    if len(buf):
      return self._bus.xfer(buf)
    return []
