# -*- coding:utf-8 -*-

import time
import RPi.GPIO as RPIGPIO

RPIGPIO.setmode(RPIGPIO.BCM)
RPIGPIO.setwarnings(False)

class GPIO:

  HIGH = RPIGPIO.HIGH
  LOW = RPIGPIO.LOW

  OUT = RPIGPIO.OUT
  IN = RPIGPIO.IN

  RISING = RPIGPIO.RISING
  FALLING = RPIGPIO.FALLING
  BOTH = RPIGPIO.BOTH

  def __init__(self, pin, mode, defaultOut = HIGH):
    self._pin = pin
    self._fInt = None
    self._intDone = True
    self._intMode = None
    if mode == self.OUT:
      RPIGPIO.setup(pin, mode)
      if defaultOut == self.HIGH:
        RPIGPIO.output(pin, defaultOut)
      else:
        RPIGPIO.output(pin, self.LOW)
    else:
      RPIGPIO.setup(pin, self.IN, pull_up_down = RPIGPIO.PUD_UP)

  def setOut(self, level):
    if level:
      RPIGPIO.output(self._pin, self.HIGH)
    else:
      RPIGPIO.output(self._pin, self.LOW)

  def _intCB(self, status):
    if self._intDone:
      self._intDone = False
      time.sleep(0.02)
      if self._intMode == self.BOTH:
        self._fInt()
      elif self._intMode == self.RISING and self.read() == self.HIGH:
        self._fInt()
      elif self._intMode == self.FALLING and self.read() == self.LOW:
        self._fInt()
      self._intDone = True

  def setInterrupt(self, mode, cb):
    if mode != self.RISING and mode != self.FALLING and mode != self.BOTH:
      return
    self._intMode = mode
    RPIGPIO.add_event_detect(self._pin, mode, self._intCB)
    self._fInt = cb

  def read(self):
    return RPIGPIO.input(self._pin)
  
  def cleanup(self):
    RPIGPIO.cleanup()
