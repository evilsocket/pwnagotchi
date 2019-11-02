#qCopyright 2013-2015 Pervasive Displays, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.  See the License for the specific language
# governing permissions and limitations under the License.


from PIL import Image
from PIL import ImageOps
from pwnagotchi.ui.hw.libs.papirus.lm75b import LM75B
import re
import os
import sys

if sys.version_info < (3,):
    def b(x):
        return x
else:
    def b(x):
        return x.encode('ISO-8859-1')

class EPDError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class EPD(object):

    """EPD E-Ink interface

to use:
  from EPD import EPD

  epd = EPD([path='/path/to/epd'], [auto=boolean], [rotation = 0|90|180|270])

  image = Image.new('1', epd.size, 0)
  # draw on image
  epd.clear()         # clear the panel
  epd.display(image)  # transfer image data
  epd.update()        # refresh the panel image - not needed if auto=true
"""


    PANEL_RE = re.compile('^([A-Za-z]+)\s+(\d+\.\d+)\s+(\d+)x(\d+)\s+COG\s+(\d+)\s+FILM\s+(\d+)\s*$', flags=0)

    def __init__(self, *args, **kwargs):
        self._epd_path = '/dev/epd'
        self._width = 200
        self._height = 96
        self._panel = 'EPD 2.0'
        self._cog = 0
        self._film = 0
        self._auto = False
        self._lm75b = LM75B()
        self._rotation = 0
        self._uselm75b = True

        if len(args) > 0:
            self._epd_path = args[0]
        elif 'epd' in kwargs:
            self._epd_path = kwargs['epd']

        if ('auto' in kwargs) and kwargs['auto']:
            self._auto = True
        if ('rotation' in kwargs):
            rot = kwargs['rotation']
            if rot in (0, 90, 180, 270):
                self._rotation = rot
            else:
                raise EPDError('rotation can only be 0, 90, 180 or 270')

        with open(os.path.join(self._epd_path, 'version')) as f:
            self._version = f.readline().rstrip('\n')

        with open(os.path.join(self._epd_path, 'panel')) as f:
            line = f.readline().rstrip('\n')
            m = self.PANEL_RE.match(line)
            if m is None:
                raise EPDError('invalid panel string')
            self._panel = m.group(1) + ' ' + m.group(2)
            self._width = int(m.group(3))
            self._height = int(m.group(4))
            self._cog = int(m.group(5))
            self._film = int(m.group(6))

        if self._width < 1 or self._height < 1:
            raise EPDError('invalid panel geometry')
        if self._rotation in (90, 270):
            self._width, self._height = self._height, self._width

    @property
    def size(self):
        return (self._width, self._height)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def panel(self):
        return self._panel

    @property
    def version(self):
        return self._version

    @property
    def cog(self):
        return self._cog

    @property
    def film(self):
        return self._film

    @property
    def auto(self):
        return self._auto

    @auto.setter
    def auto(self, flag):
        if flag:
            self._auto = True
        else:
            self._auto = False

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, rot):
        if rot not in (0, 90, 180, 270):
            raise EPDError('rotation can only be 0, 90, 180 or 270')
        if abs(self._rotation - rot) == 90 or abs(self._rotation - rot) == 270:
            self._width, self._height = self._height, self._width
        self._rotation = rot

    @property
    def use_lm75b(self):
        return self._uselm75b

    @use_lm75b.setter
    def use_lm75b(self, flag):
        if flag:
            self._uselm75b = True
        else:
            self._uselm75b = False

    def error_status(self):
        with open(os.path.join(self._epd_path, 'error'), 'r') as f:
            return(f.readline().rstrip('\n'))

    def rotation_angle(self, rotation):
        angles = { 90 : Image.ROTATE_90, 180 : Image.ROTATE_180, 270 : Image.ROTATE_270 }
        return angles[rotation]

    def display(self, image):

        # attempt grayscale conversion, and then to single bit
        # better to do this before calling this if the image is to
        # be displayed several times
        if image.mode != "1":
            image = ImageOps.grayscale(image).convert("1", dither=Image.FLOYDSTEINBERG)

        if image.mode != "1":
            raise EPDError('only single bit images are supported')

        if image.size != self.size:
            raise EPDError('image size mismatch')

        if self._rotation != 0:
            image = image.transpose(self.rotation_angle(self._rotation))

        with open(os.path.join(self._epd_path, 'LE', 'display_inverse'), 'r+b') as f:
            f.write(image.tobytes())

        if self.auto:
            self.update()


    def update(self):
        self._command('U')

    def partial_update(self):
        self._command('P')

    def fast_update(self):
        self._command('F')

    def clear(self):
        self._command('C')

    def _command(self, c):
        if self._uselm75b:
            with open(os.path.join(self._epd_path, 'temperature'), 'wb') as f:
                f.write(b(repr(self._lm75b.getTempC())))
        with open(os.path.join(self._epd_path, 'command'), 'wb') as f:
            f.write(b(c))
