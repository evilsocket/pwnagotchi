import logging

import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.hw.base import DisplayImpl

class DFRobotV2(DisplayImpl):
  def __init__(self, config):
    super(DFRobotV2, self).__init__(config, 'dfrobot_2')
    self._display = None

  def layout(self):
    fonts.setup(10, 9, 10, 35, 25, 9)
    self._layout['width'] = 250
    self._layout['height'] = 122
    self._layout['face'] = (0, 40)
    self._layout['name'] = (5, 20)
    self._layout['channel'] = (0, 0)
    self._layout['aps'] = (28, 0)
    self._layout['uptime'] = (185, 0)
    self._layout['line1'] = [0, 14, 250, 14]
    self._layout['line2'] = [0, 108, 250, 108]
    self._layout['friend_face'] = (0, 92)
    self._layout['friend_name'] = (40, 94)
    self._layout['shakes'] = (0, 109)
    self._layout['mode'] = (225, 109)
    self._layout['status'] = {
        'pos': (125, 20),
        'font': fonts.status_font(fonts.Medium),
        'max': 20
    }
    return self._layout

  def initialize(self):
    logging.info("initializing dfrobot2 display")
    from pwnagotchi.ui.hw.libs.dfrobot.v2.dfrobot import DFRobot
    self._display = DFRobot()

  def render(self, canvas):
    buf = self._display.getbuffer(canvas)
    self._display.display(buf)

  def clear(self):
    self._display.Clear(0xFF)
