# -*- coding:utf-8 -*-

'''
depends: freetype-py
'''

import freetype
import math
#import sys

#reload(sys)
#sys.setdefaultencoding("utf-8")
import importlib,sys

#importlib.reload(sys)
class Freetype_Helper:

  def __init__(self, filePath):
    self._face = freetype.Face(filePath)
    self._width = 0
    self._height = 0
    self._fade = 96

  def setFmt(self, width, height):
    self._width = int(width)
    self._height = int(height)
    self._face.set_pixel_sizes(width, height)
  
  def setDisLowerLimite(self, limite):
    self._fade = limite

  def getOne(self, ch):
    self._face.load_char(ch)
    bitmap = self._face.glyph.bitmap
    originY = self._face.glyph.bitmap_top
    width = bitmap.width
    height = bitmap.rows
    buffer = bitmap.buffer
    rslt = []

    # width = 4
    # height = 4
    # buffer = [0xff] * width * height

    if height > self._height:
      buffer = buffer[0: width * self._height]
      height = self._height
    if width > self._width:
      for i in range(height):
        rslt += buffer[i * width: i * width + self._width]
      width = self._width
      buffer = rslt
      rslt = []
    if (ord(ch) >= ord(" ") and ord(ch) <= ord("~")) or width <= (self._width // 2):
      rslt = [0] * (((self._width - 1) // 16 + 1) * self._height + 1)
      left = (self._width // 2 - width) // 2
      lineDataLen = (self._width - 1) // 16 + 1
    else:
      rslt = [0] * (((self._width - 1) // 8 + 1) * self._height + 1)
      left = (self._width - width) // 2
      lineDataLen = (self._width - 1) // 8 + 1
    if left < 0:
      left = 0
    # top = (self._height - height) * lineDataLen // 2
    top = ((self._height * 8 + 5) // 10 - originY) * lineDataLen
    if top < 0:
      top = 0
    for i in range(height):
      for j in range(width):
        if buffer[i * width + j] > self._fade:
          try:
            rslt[i * lineDataLen + (j + left) // 8 + top] |= 0x80 >> ((j + left) % 8)
          except:
            print("freetype_helper getOne err: width: %d, height: %d, top: %d, left: %d, rslt_len: %d, originY: %d" %(width, height, top, left, len(rslt), originY))
            raise("err")
          # rslt[i * lineDataLen + (j + left) // 8 + top] |= 0x80 >> ((j + left) % 8)
    if (ord(ch) >= ord(" ") and ord(ch) <= ord("~")) or width < (self._width // 2):
      return (rslt, self._width // 2, self._height, "TBMLLR")
    else:
      return (rslt, self._width, self._height, "TBMLLR")
