FBIOGET_VSCREENINFO=0x4600
FBIOPUT_VSCREENINFO=0x4601
FBIOGET_FSCREENINFO=0x4602
FBIOGETCMAP=0x4604
FBIOPUTCMAP=0x4605
FBIOPAN_DISPLAY=0x4606

FBIOGET_CON2FBMAP=0x460F
FBIOPUT_CON2FBMAP=0x4610
FBIOBLANK=0x4611
FBIO_ALLOC=0x4613
FBIO_FREE=0x4614
FBIOGET_GLYPH=0x4615
FBIOGET_HWCINFO=0x4616
FBIOPUT_MODEINFO=0x4617
FBIOGET_DISPINFO=0x4618

from mmap import mmap
from fcntl import ioctl
import struct

mm = None
bpp, w, h = 0, 0, 0 # framebuffer bpp and size
bytepp = 0
vx, vy, vw, vh = 0, 0, 0, 0 #virtual window offset and size
vi, fi = None, None
_fb_cmap = 'IIPPPP' # start, len, r, g, b, a
RGB = False
_verbose = False
msize_kb = 0

def report_fb(i=0, layer=0):
  with open('/dev/fb'+str(i), 'r+b')as f:
    vi = ioctl(f, FBIOGET_VSCREENINFO, bytes(160))
    vi = list(struct.unpack('I'*40, vi))
    ffm = 'c'*16+'L'+'I'*4+'H'*3+'ILIIHHH'
    fic = struct.calcsize(ffm)
    fi = struct.unpack(ffm, ioctl(f, FBIOGET_FSCREENINFO, bytes(fic)))

def ready_fb(_bpp=None, i=0, layer=0, _win=None):
  global mm, bpp, w, h, vi, fi, RGB, msize_kb, vx, vy, vw, vh, bytepp
  if mm and bpp == _bpp: return mm, w, h, bpp
  with open('/dev/fb'+str(i), 'r+b')as f:
    vi = ioctl(f, FBIOGET_VSCREENINFO, bytes(160))
    vi = list(struct.unpack('I'*40, vi))
    bpp = vi[6]
    bytepp = bpp//8
    if _bpp:
      vi[6] = _bpp # 24 bit = BGR 888 mode
      try:
        vi = ioctl(f, FBIOPUT_VSCREENINFO, struct.pack('I'*40, *vi)) # fb_var_screeninfo
        vi = struct.unpack('I'*40,vi)
        bpp = vi[6]
        bytepp = bpp//8
      except:
        pass
    
    if vi[8] == 0 : RGB = True
    
    ffm = 'c'*16+'L'+'I'*4+'H'*3+'ILIIHHH'
    fic = struct.calcsize(ffm)
    fi = struct.unpack(ffm, ioctl(f, FBIOGET_FSCREENINFO, bytes(fic)))
    msize = fi[17] # = w*h*bpp//8
    ll, start = fi[-7:-5]
    w, h = ll//bytepp, vi[1] # when screen is vertical, width becomes wrong. ll//3 is more accurate at such time.
    if _win and len(_win)==4: # virtual window settings
      vx, vy, vw, vh = _win
      if vw == 'w': vw = w
      if vh == 'h': vh = h
      vx, vy, vw, vh = map(int, (vx, vy, vw, vh))
      if vx>=w: vx = 0
      if vy>=h: vy = 0
      if vx>w: vw = w - vx
      else: vw -= vx
      if vy>h: vh = h - vy
      else: vh -= vy
    else:
      vx, vy, vw, vh = 0,0,w,h
    msize_kb = vw*vh*bytepp//1024 # more accurate FB memory size in kb

    mm = mmap(f.fileno(), msize, offset=start)
    return mm, w, h, bpp#ll//(bpp//8), h

def fill_scr(r,g,b):
  if bpp == 32:
    seed = struct.pack('BBBB', b, g, r, 255)
  elif bpp == 24:
    seed = struct.pack('BBB', b, g, r)
  elif bpp == 16:
    seed = struct.pack('H', r>>3<<11 | g>>2<<5 | b>>3)
  mm.seek(0)
  show_img(seed * vw * vh)

def black_scr():
  fill_scr(0,0,0)

def white_scr():
  fill_scr(255,255,255)

def mmseekto(x,y):
  mm.seek((x + y*w) * bytepp)

def dot(x, y, r, g, b):
  mmseekto(x,y)
  mm.write(struct.pack('BBB',*((r,g,b) if RGB else (b,g,r))))

def get_pixel(x,y):
  mmseekto(x,y)
  return mm.read(bytepp)

def _888_to_565(bt):
  b = b''
  for i in range(0, len(bt),3):
    b += int.to_bytes(bt[i]>>3<<11|bt[i+1]>>2<<5|bt[i+2]>>3, 2, 'little')
  return b

def numpy_888_565(bt):
  import numpy as np
  arr = np.fromstring(bt, dtype=np.uint32)
  return (((0xF80000 & arr)>>8)|((0xFC00 & arr)>>5)|((0xF8 & arr)>>3)).astype(np.uint16).tostring()

def show_img(img):
  if not type(img) is bytes:
    if not RGB:
      if bpp == 24: # for RPI
        img = img.tobytes('raw', 'BGR')
      else:
        img = img.convert('RGBA').tobytes('raw', 'BGRA')
        if bpp == 16:
          img = numpy_888_565(img)
    else:
      if bpp == 24:
        img = img.tobytes()
      else:
        img = img.convert('RGBA').tobytes()
        if bpp == 16:
          img = numpy_888_565(img)
  from io import BytesIO
  b = BytesIO(img)
  s = vw*bytepp
  for y in range(vh): # virtual window drawing
    mmseekto(vx,vy+y)
    mm.write(b.read(s))

