# -*- coding:utf-8 -*-

import sys

from .dfrobot_printString import PrintString
from .dfrobot_fonts import Fonts

def color24to16(color):
    return (((color >> 8) & 0xf800) | ((color >> 5) & 0x7e0) | ((color >> 3) & 0x1f))

def color16to24(color):
    return (((color & 0xf800) << 8) | ((color & 0x7e0) << 5) | ((color & 0x1f) << 3))

def swap(o1, o2):
    return (o2, o1)

class DFRobot_Display(PrintString):

  WHITE24 = 0xffffff
  SILVER24 = 0xc0c0c0
  GRAY24 = 0x808080
  BLACK24 = 0x000000
  RED24 = 0xff0000
  MAROON24 = 0x800000
  YELLOW24 = 0xffff00
  OLIVE24 = 0x808000
  GREEN24 = 0x00ff00
  DARKGREEN24 = 0x008000
  CYAN24 = 0x00ffff
  BLUE24 = 0x0000ff
  NAVY24 = 0x000080
  FUCHSIA24 = 0xff00ff
  PURPLE24 = 0x800080
  TEAL24 = 0x008080

  WHITE16 = color24to16(WHITE24)
  SILVER16 = color24to16(SILVER24)
  GRAY16 = color24to16(GRAY24)
  BLACK16 = color24to16(BLACK24)
  RED16 = color24to16(RED24)
  MAROON16 = color24to16(MAROON24)
  YELLOW16 = color24to16(YELLOW24)
  OLIVE16 = color24to16(OLIVE24)
  GREEN16 = color24to16(GREEN24)
  DARKGREEN16 = color24to16(DARKGREEN24)
  CYAN16 = color24to16(CYAN24)
  BLUE16 = color24to16(BLUE24)
  NAVY16 = color24to16(NAVY24)
  FUCHSIA16 = color24to16(FUCHSIA24)
  PURPLE16 = color24to16(PURPLE24)
  TEAL16 = color24to16(TEAL24)

  WHITE = WHITE16
  SILVER = SILVER16
  GRAY = GRAY16
  BLACK = BLACK16
  RED = RED16
  MAROON = MAROON16
  YELLOW = YELLOW16
  OLIVE = OLIVE16
  GREEN = GREEN16
  DARKGREEN = DARKGREEN16
  CYAN = CYAN16
  BLUE = BLUE16
  NAVY = NAVY16
  FUCHSIA = FUCHSIA16
  PURPLE = PURPLE16
  TEAL = TEAL16

  POSITIVE = 1
  REVERSE = -1

  BITMAP_TBMLLR = "TBMLLR"
  BITMAP_TBMRLL = "TBMRLL"
  BITMAP_BTMLLR = "BTMLLR"
  BITMAP_BTMRLL = "BTMRLL"
  BITMAP_LRMTLB = "LRMTLB"
  BITMAP_LRMBLT = "LRMBLT"
  BITMAP_RLMTLB = "RLMTLB"
  BIMTAP_RLMBLT = "RLMBLT"
  BITMAP_UNKNOW = "UNKNOW"

  def __init__(self, w, h):
    PrintString.__init__(self)
    print("DFRobot_Display init " + str(w) + " " + str(h))
    self._width = w
    self._height = h

    self._lineWidth = 1
    self._bitmapSize = 1
    self._bitmapFmt = ""
    self._bmpFmt = self.BITMAP_TBMLLR

    self._fonts = Fonts()
    self._textSize = 1
    self._textColor = self.BLACK
    self._textBackground = self.WHITE
    self._textCursorX = 0
    self._textCursorY = 0
    self._textIntervalRow = 0
    self._textIntervalCol = 0

  def _ternaryExpression(self, condition, o1, o2):
    if condition:
      return o1
    return o2

  def _getDirection(self, value):
    if value >= 0:
      return 1
    return -1

  def color16to24(self, color):
    return color16to24(color)

  def color24to16(self, color):
    return color24to16(color)

  def setColorTo16(self):
    self.WHITE = self.WHITE16
    self.SILVER = self.SILVER16
    self.GRAY = self.GRAY16
    self.BLACK = self.BLACK16
    self.RED = self.RED16
    self.MAROON = self.MAROON16
    self.YELLOW = self.YELLOW16
    self.OLIVE = self.OLIVE16
    self.GREEN = self.GREEN16
    self.DARKGREEN = self.DARKGREEN16
    self.CYAN = self.CYAN16
    self.BLUE = self.BLUE16
    self.NAVY = self.NAVY16
    self.FUCHSIA = self.FUCHSIA16
    self.PURPLE = self.PURPLE16
    self.TEAL = self.TEAL16

  def setColorTo24(self):
    self.WHITE = self.WHITE24
    self.SILVER = self.SILVER24
    self.GRAY = self.GRAY24
    self.BLACK = self.BLACK24
    self.RED = self.RED24
    self.MAROON = self.MAROON24
    self.YELLOW = self.YELLOW24
    self.OLIVE = self.OLIVE24
    self.GREEN = self.GREEN24
    self.DARKGREEN = self.DARKGREEN24
    self.CYAN = self.CYAN24
    self.BLUE = self.BLUE24
    self.NAVY = self.NAVY24
    self.FUCHSIA = self.FUCHSIA24
    self.PURPLE = self.PURPLE24
    self.TEAL = self.TEAL24

  def setLineWidth(self, w):
    if w < 0:
      return
    self._lineWidth = w

  def setTextFormat(self, size, color, background, intervalRow = 2, intervalCol = 0):
    self._textColor = color
    self._textIntervalRow = intervalRow
    self._textIntervalCol = intervalCol
    self._textBackground = background
    if size < 0:
      return
    self._textSize = size

  def setTextCursor(self, x, y):
    self._textCursorX = int(x)
    self._textCursorY = int(y)

  def setBitmapSize(self, size):
    if size < 0:
      return
    self._bitmapSize = size

  def setBitmapFmt(self, fmt):
    self._bmpFmt = fmt

  def setExFonts(self, obj):
    self._fonts.setExFonts(obj)

  def setExFontsFmt(self, width, height):
    self._fonts.setExFontsFmt(width, height)
    
  def setEnableDefaultFonts(self, opt):
    self._fonts.setEnableDefaultFonts(opt)

  def pixel(self, x, y, color):
    pass

  def clear(self, color):
    self.fillRect(0, 0, self._width, self._height, color)
    self._textCursorX = 0
    self._textCursorY = 0

  def VLine(self, x, y, h, color):
    x = int(x)
    y = int(y)
    h = int(h)
    direction = self._getDirection(h)
    x -= self._lineWidth // 2
    h = self._ternaryExpression(h > 0, h, -h)
    for i in range(self._ternaryExpression(h > 0, h, - h)):
      xx = x
      for j in range(self._lineWidth):
        self.pixel(xx, y, color)
        xx += 1
      y += direction

  def HLine(self, x, y, w, color):
    x = int(x)
    y = int(y)
    w = int(w)
    direction = self._getDirection(w)
    y -= self._lineWidth // 2
    for i in range(self._ternaryExpression(w > 0, w, - w)):
      yy = y
      for j in range(self._lineWidth):
        self.pixel(x, yy, color)
        yy += 1
      x += direction

  def line(self, x, y, x1, y1, color):
    x = int(x)
    y = int(y)
    x1 = int(x1)
    y1 = int(y1)
    if x == x1:
      self.VLine(x, y, y1 - y, color)
      return
    if y == y1:
      self.HLine(x, y, x1 - x, color)
      return
    dx = abs(x1 - x)
    dy = abs(y1 - y)
    dirX = self._ternaryExpression(x < x1, 1, -1)
    dirY = self._ternaryExpression(y < y1, 1, -1)
    if dx > dy:
      err = dx / 2
      for i in range(dx):
        self.HLine(x, y, 1, color)
        x += dirX
        err -= dy
        if err < 0:
          err += dx
          y += dirY
      self.HLine(x1, y1, 1, color)
    else:
      err = dy / 2
      for i in range(dy):
        self.VLine(x, y, 1, color)
        y += dirY
        err -= dx
        if err < 0:
          err += dy
          x += dirX
      self.VLine(x1, y1, 1, color)

  def triangle(self, x, y, x1, y1, x2, y2, color):
    self.line(x, y, x1, y1, color)
    self.line(x1, y1, x2, y2, color)
    self.line(x2, y2, x, y, color)

  def fillTriangle(self, x, y, x1, y1, x2, y2, color):
    self.line(x, y, x1, y1, color)
    self.line(x1, y1, x2, y2, color)
    self.line(x2, y2, x, y, color)
    x = int(x)
    y = int(y)
    x1 = int(x1)
    y1 = int(y1)
    x2 = int(x2)
    y2 = int(y2)
    temp = self._lineWidth
    self._lineWidth = 1
    if x == x1 and x == x2:
      ymax = max([y, y1, y2])
      ymin = min([y, y1, y2])
      self.HLine(x, ymin, ymax - ymin, color)
      self._lineWidth = temp
      return
    if y == y1 and y == y2:
      xmax = max([x, x1, x2])
      xmin = max([x, x1, x2])
      self.VLine(xmin, y, xmax - xmin, color)
      self._lineWidth = temp
      return

    direction = self.POSITIVE
    if y == y1 or y1 == y2 or y == y2:
      if y == y1:
        (x, x2) = swap(x, x2)
        (y, y2) = swap(y, y2)
      elif y == y2:
        (x, x1) = swap(x, x1)
        (y, y1) = swap(y, y1)
      if y > y1:
        direction = self.REVERSE
      if x1 > x2:
        (x1, x2) = swap(x1, x2)
        (y1, y2) = swap(y1, y2)
    else:
      if y > y1:
        (x, x1) = swap(x, x1)
        (y, y1) = swap(y, y1)
      if y > y2:
        (x, x2) = swap(x, x2)
        (y, y2) = swap(y, y2)
      if y1 > y2:
        (x1, x2) = swap(x1, x2)
        (y1, y2) = swap(y1, y2)

    dx1 = x1 - x
    dx2 = x2 - x
    dx3 = x2 - x1
    dy1 = y1 - y
    dy2 = y2 - y
    dy3 = y2 - y1
    if direction == self.POSITIVE:
      for i in range(dy1):
        self.HLine(x + dx1 * i / dy1, y + i, (x + dx2 * i / dy2) - (x + dx1 * i / dy1) + 1, color)
      for i in range(dy3):
        self.HLine(x1 + dx3 * i / dy3, y1 + i, (x + dx2 * (i + dy1) / dy2) - (x1 + dx3 * i / dy3) + 1, color)
    else:
      y = y1 + dy1
      dy1 = - dy1
      for i in range(dy1):
        self.HLine(x + dx1 * i / dy1, y1 + dy1 - i, (x + dx2 * i / dy1) - (x + dx1 * i / dy1) + 1, color)
    self._lineWidth = temp

  def rect(self, x, y, w, h, color):
    if w < 0:
      x += w
      w = -w
    if h < 0:
      y += h
      h = -h
    self.HLine(x - self._lineWidth // 2, y, w + self._lineWidth, color)
    self.HLine(x - self._lineWidth // 2, y + h, w + self._lineWidth, color)
    self.VLine(x, y - self._lineWidth // 2, h + self._lineWidth, color)
    self.VLine(x + w, y - self._lineWidth // 2, h + self._lineWidth, color)

  def fillRect(self, x, y, w, h, color):
    temp = self._lineWidth
    self._lineWidth = 1
    if w < 0:
      x += w
      w = abs(w)
    for i in range(w):
      self.VLine(x + i, y, h, color)
    self._lineWidth = temp

  QUADRANT_1 = 1
  QUADRANT_2 = 2
  QUADRANT_3 = 4
  QUADRANT_4 = 8
  QUADRANT_ALL = 15

  def circleHelper(self, x, y, r, quadrant, color):
    x = int(x)
    y = int(y)
    r = abs(int(r))
    vx = 0
    vy = r
    dx = 1
    dy = -2 * r
    p = 1 - r
    if quadrant & self.QUADRANT_1:
      self.VLine(x + r, y, 1, color)
    if quadrant & self.QUADRANT_2:
      self.VLine(x, y - r, 1, color)
    if quadrant & self.QUADRANT_3:
      self.VLine(x - r, y, 1, color)
    if quadrant & self.QUADRANT_4:
      self.VLine(x, y + r, 1, color)
    
    halfLineWidth = self._lineWidth // 2
    while vx < vy:
      if p >= 0:
        vy -= 1
        dy += 2
        p += dy
      vx += 1
      dx += 2
      p += dx
      if quadrant & self.QUADRANT_1:
        self.fillRect(x + vx - halfLineWidth, y - vy - halfLineWidth, self._lineWidth, self._lineWidth, color)  # quadrant 1
        self.fillRect(x + vy - halfLineWidth, y - vx - halfLineWidth, self._lineWidth, self._lineWidth, color)  # quadrant 1
      if quadrant & self.QUADRANT_2:
        self.fillRect(x - vx - halfLineWidth, y - vy - halfLineWidth, self._lineWidth, self._lineWidth, color)  # quadrant 2
        self.fillRect(x - vy - halfLineWidth, y - vx - halfLineWidth, self._lineWidth, self._lineWidth, color)  # quadrant 2
      if quadrant & self.QUADRANT_3:
        self.fillRect(x - vx - halfLineWidth, y + vy - halfLineWidth, self._lineWidth, self._lineWidth, color)  # quadrant 3
        self.fillRect(x - vy - halfLineWidth, y + vx - halfLineWidth, self._lineWidth, self._lineWidth, color)  # quadrant 3
      if quadrant & self.QUADRANT_4:
        self.fillRect(x + vx - halfLineWidth, y + vy - halfLineWidth, self._lineWidth, self._lineWidth, color)  # quadrant 4
        self.fillRect(x + vy - halfLineWidth, y + vx - halfLineWidth, self._lineWidth, self._lineWidth, color)  # quadrant 4

  def circle(self, x, y, r, color):
    self.circleHelper(x, y, r, self.QUADRANT_ALL, color)

  def fillCircleHelper(self, x, y, r, quadrant, color):
    x = int(x)
    y = int(y)
    r = abs(int(r))
    temp = self._lineWidth
    self._lineWidth = 1
    vx = 0
    vy = r
    dx = 1
    dy = -2 * r
    p = 1 - r
    if quadrant & self.QUADRANT_1:
      self.HLine(x, y, r + 1, color)
    if quadrant & self.QUADRANT_2:
      self.VLine(x, y, - r - 1, color)
    if quadrant & self.QUADRANT_3:
      self.HLine(x, y, - r - 1, color)
    if quadrant & self.QUADRANT_4:
      self.VLine(x, y, r + 1, color)

    while vx < vy:
      if p >= 0:
        vy -= 1
        dy += 2
        p += dy
      vx += 1
      dx += 2
      p += dx
      if quadrant & self.QUADRANT_1:
        self.VLine(x + vx, y - vy, vy, color)  # quadrant 1
        self.VLine(x + vy, y - vx, vx, color)  # quadrant 1
      if quadrant & self.QUADRANT_2:
        self.VLine(x - vx, y - vy, vy, color)  # quadrant 2
        self.VLine(x - vy, y - vx, vx, color)  # quadrant 2
      if quadrant & self.QUADRANT_3:
        self.VLine(x - vx, y + vy, - vy, color)  # quadrant 3
        self.VLine(x - vy, y + vx, - vx, color)  # quadrant 3
      if quadrant & self.QUADRANT_4:
        self.VLine(x + vx, y + vy, - vy, color)  # quadrant 4
        self.VLine(x + vy, y + vx, - vx, color)  # quadrant 4
    self._lineWidth = temp

  def fillCircle(self, x, y, r, color):
    self.fillCircleHelper(x, y, r, self.QUADRANT_ALL, color)

  def roundRect(self, x, y, w, h, r, color):
    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)
    r = abs(int(r))
    if w < 0:
      x += w
      w = abs(w)
    if h < 0:
      y += h
      h = abs(h)
    self.HLine(x + r, y, w - 2 * r + 1, color)
    self.HLine(x + r, y + h, w - 2 * r + 1, color)
    self.VLine(x, y + r, h - 2 * r + 1, color)
    self.VLine(x + w, y + r, h - 2 * r + 1, color)
    self.circleHelper(x + r, y + r, r, self.QUADRANT_2, color)
    self.circleHelper(x + w - r, y + r, r, self.QUADRANT_1, color)
    self.circleHelper(x + r, y + h - r, r, self.QUADRANT_3, color)
    self.circleHelper(x + w - r, y + h - r, r, self.QUADRANT_4, color)

  def fillRoundRect(self, x, y, w, h, r, color):
    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)
    r = abs(int(r))
    if w < 0:
      x += w
      w = abs(w)
    if h < 0:
      y += h
      h = abs(h)
    self.fillRect(x + r, y, w - 2 * r, h, color)
    self.fillRect(x, y + r, r, h - 2 * r, color)
    self.fillRect(x + w - r, y + r, r, h - 2 * r, color)
    self.fillCircleHelper(x + r, y + r, r, self.QUADRANT_2, color)
    self.fillCircleHelper(x + w - r - 1, y + r, r, self.QUADRANT_1, color)
    self.fillCircleHelper(x + r, y + h - r - 1, r, self.QUADRANT_3, color)
    self.fillCircleHelper(x + w - r - 1, y + h - r - 1, r, self.QUADRANT_4, color)

  def _bitmapHelper(self, increaseAxis, staticAxis, data, dataBit, exchange, color, background):
    for i in data:
      for j in range(8):
        if i & dataBit:
          if exchange:
            self.fillRect(staticAxis, increaseAxis, self._bitmapSize, self._bitmapSize, color)
          else:
            self.fillRect(increaseAxis, staticAxis, self._bitmapSize, self._bitmapSize, color)
        else:
          if exchange:
            self.fillRect(staticAxis, increaseAxis, self._bitmapSize, self._bitmapSize, background)
          else:
            self.fillRect(increaseAxis, staticAxis, self._bitmapSize, self._bitmapSize, background)
        increaseAxis += self._bitmapSize
        if dataBit & 0x80:
          i <<= 1
        else:
          i >>= 1

  def bitmap(self, x, y, bitmap, w, h, color, background):
    if w < 0 or h < 0:
      return
    x = abs(int(x))
    y = abs(int(y))

    if self._bmpFmt == self.BITMAP_TBMLLR:
      oneLineDataLen = (w - 1) // 8 + 1
      for i in range(h):
        yMask = y + i * self._bitmapSize
        self._bitmapHelper(x, yMask, bitmap[i * oneLineDataLen : oneLineDataLen * (i + 1)], 0x80, False, color, background)
    elif self._bmpFmt == self.BITMAP_TBMRLL:
      oneLineDataLen = (w - 1) // 8 + 1
      for i in range(h):
        yMask = y + i * self._bitmapSize
        self._bitmapHelper(x, yMask, bitmap[i * oneLineDataLen : oneLineDataLen * (i + 1)], 0x01, False, color, background)
    elif self._bmpFmt == self.BITMAP_BTMLLR:
      oneLineDataLen = (w - 1) // 8 + 1
      for i in range(h):
        yMask = y + h * self._bitmapSize - i * self._bitmapSize
        self._bitmapHelper(x, yMask, bitmap[i * oneLineDataLen : oneLineDataLen * (i + 1)], 0x80, False, color, background)
    elif self._bmpFmt == self.BITMAP_BTMRLL:
      oneLineDataLen = (w - 1) // 8 + 1
      for i in range(h):
        yMask = y + h * self._bitmapSize - i * self._bitmapSize
        self._bitmapHelper(x, yMask, bitmap[i * oneLineDataLen : oneLineDataLen * (i + 1)], 0x01, False, color, background)
    elif self._bmpFmt == self.BITMAP_LRMTLB:
      oneLineDataLen = (h - 1) // 8 + 1
      for i in range(w):
        xMask = x + i * self._bitmapSize
        self._bitmapHelper(y, xMask, bitmap[i * oneLineDataLen : oneLineDataLen * (i + 1)], 0x80, True, color, background)
    elif self._bmpFmt == self.BITMAP_LRMBLT:
      oneLineDataLen = (h - 1) // 8 + 1
      for i in range(w):
        xMask = x + i * self._bitmapSize
        self._bitmapHelper(y, xMask, bitmap[i * oneLineDataLen : oneLineDataLen * (i + 1)], 0x01, True, color, background)
    elif self._bmpFmt == self.BITMAP_RLMTLB:
      oneLineDataLen = (h - 1) // 8 + 1
      for i in range(w):
        xMask = x + w * self._bitmapSize - i * self._bitmapSize
        self._bitmapHelper(y, xMask, bitmap[i * oneLineDataLen : oneLineDataLen * (i + 1)], 0x80, True, color, background)
    elif self._bmpFmt == self.BIMTAP_RLMBLT:
      oneLineDataLen = (h - 1) // 8 + 1
      for i in range(w):
        xMask = x + w * self._bitmapSize - i * self._bitmapSize
        self._bitmapHelper(y, xMask, bitmap[i * oneLineDataLen : oneLineDataLen * (i + 1)], 0x01, True, color, background)

  def _bytesToNumber(self, data):
    r = 0
    i = len(data)
    while i > 0:
      i -= 1
      r = r << 8 | data[i]
    return r

  def _getQuads(self, data, count):
    r = []
    for i in range(count):
      r.append(data[i * 4 + 54 : i * 4 + 58])
    return r

  BITMAP_COMPRESSION_NO = 0
  BITMAP_COMPRESSION_RLE8 = 1
  BITMAP_COMPRESSION_RLE4 = 2
  BITMAP_COMPRESSION_FIELDS = 3

  def startDrawBitmapFile(self, x, y):
    pass
  
  def bitmapFileHelper(self, buf):
    pass

  def endDrawBitmapFile(self):
    pass

  def bitmapFile(self, x, y, path):
    try:
      f = open(path, "rb")
    except:
      print("open file error")
      return
    c = bytearray(f.read())
    f.close()
    if c[0] != 0x42 and c[1] != 0x4d:
      print("file error")
      print(c[0])
      print(c[1])
      return
    DIBOffset = self._bytesToNumber(c[10:14])
    width = self._bytesToNumber(c[18:22])
    height = self._bytesToNumber(c[22:26])
    colorBits = self._bytesToNumber(c[28:30])
    compression = self._bytesToNumber(c[30:32])
    # print("w: %d, h: %d, colorBits: %d" %(width, height, colorBits))

    if colorBits == 24:
      width3 = width * 3
      for i in range(height):
        self.startDrawBitmapFile(x, y + height - i)
        buf = []
        left = DIBOffset + i * width3
        i = 0
        while i < width3:
          buf.append(c[left + i + 2])
          buf.append(c[left + i + 1])
          buf.append(c[left + i + 0])
          i += 3
        self.bitmapFileHelper(buf)
      self.endDrawBitmapFile()

    elif colorBits == 1:
      quads = self._getQuads(c, 2)
      addr = DIBOffset
      if compression == self.BITMAP_COMPRESSION_NO:
        addrCountComplement = (width // 8 + 1) % 4
        if addrCountComplement != 0:
          addrCountComplement = 4 - addrCountComplement
        for i in range(height):
          w = width
          addrCount = 0
          self.startDrawBitmapFile(x, y + height - i - 1)
          buf = []
          while w > 0:
            d = c[addr + addrCount]
            addrCount = addrCount + 1
            j = 8
            while w > 0 and j > 0:
              j -= 1
              quad = d & (0x01 << j)
              if quad > 0:
                quad = 1
              buf.append(quads[quad][2])
              buf.append(quads[quad][1])
              buf.append(quads[quad][0])
              w -= 1
          self.bitmapFileHelper(buf)
          addrCount += addrCountComplement
          addr += addrCount
        self.endDrawBitmapFile()
    else:
      print("dont support this bitmap file format yet")

  def writeOneChar(self, c):
    if len(c) > 1:
      c = c[0]
    (l, width, height, fmt) = self._fonts.getOneCharacter(c)
    temp = self._bmpFmt
    self._bmpFmt = fmt
    ts = self._textSize
    if ord(c) == ord("\n"):
      self._textCursorX = 0
      self._textCursorY += height * ts + self._textIntervalCol
    elif len(l):
      temp1 = self._bitmapSize
      self._bitmapSize = ts
      self._textCursorX += self._textIntervalRow
      if self._textCursorX + ts * width > self._width:
        self.fillRect(self._textCursorX, self._textCursorY, self._width - self._textCursorX, self._fonts._extensionFontsHeight * ts + self._textIntervalCol, self._textBackground)
        self._textCursorX = self._textIntervalRow
        self._textCursorY += ts * self._fonts._extensionFontsHeight + self._textIntervalCol
      self.fillRect(self._textCursorX, self._textCursorY, self._fonts._extensionFontsWidth * ts + self._textIntervalRow, self._fonts._extensionFontsHeight * ts + self._textIntervalCol, self._textBackground)
      self.bitmap(self._textCursorX, self._textCursorY, l, width, height, self._textColor, self._textBackground)
      self._textCursorX += ts * width
      self._bitmapSize = temp1
    self._bmpFmt = temp
