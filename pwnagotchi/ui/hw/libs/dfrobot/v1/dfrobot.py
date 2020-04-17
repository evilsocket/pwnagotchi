# DFRobot display support

import logging
from . import dfrobot_epaper

#Resolution of display
WIDTH = 250
HEIGHT = 122

RASPBERRY_SPI_BUS = 0
RASPBERRY_SPI_DEV = 0
RASPBERRY_PIN_CS = 27
RASPBERRY_PIN_CD = 17
RASPBERRY_PIN_BUSY = 4

class DFRobot:
  def __init__(self):
    self._display = dfrobot_epaper.DFRobot_Epaper_SPI(RASPBERRY_SPI_BUS, RASPBERRY_SPI_DEV, RASPBERRY_PIN_CS, RASPBERRY_PIN_CD, RASPBERRY_PIN_BUSY)
    self._display.begin()
    self.clear(0xFF)
    self.FULL = self._display.FULL
    self.PART = self._display.PART

  def getbuffer(self, image):
    if HEIGHT % 8 == 0:
      linewidth = HEIGHT // 8
    else:
      linewidth = HEIGHT // 8 + 1

    buf = [0xFF] * (linewidth * WIDTH)
    image_monocolor = image.convert('1')
    imwidth, imheight = image_monocolor.size
    pixels = image_monocolor.load()

    if (imwidth == HEIGHT and imheight == WIDTH):
      for y in range(imheight):
        for x in range(imwidth):
          if pixels[x,y] == 0:
            x = imwidth - x
            buf[x // 8 + y * linewidth] &= ~(0x80 >> (x % 8))
    elif (imwidth == WIDTH and imheight == HEIGHT):
      for y in range(imheight):
        for x in range(imwidth):
          newx = y
          newy = WIDTH - x - 1
          if pixels[x,y] == 0:
            newy = imwidth - newy - 1
            buf[newx // 8 + newy * linewidth] &= ~(0x80 >> (y % 8))
    return buf
  
  def flush(self, type):
    self._display.flush(type)

  def display(self, buf):
    self._display.setBuffer(buf)
    self.flush(self._display.PART)

  def clear(self, color):
    if HEIGHT % 8 == 0:
      linewidth = HEIGHT // 8
    else:
      linewidth = HEIGHT // 8 + 1

    buf = [color] * (linewidth * WIDTH)
    self._display.setBuffer(buf)
    self.flush(self._display.FULL)
