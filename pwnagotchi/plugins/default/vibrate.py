__author__ = 'pwnagotchi [at] rossmarks [dot] uk'
__version__ = '1.0.0'
__name__ = 'vibrate'
__license__ = 'GPL3'
__description__ = 'quick vibrate once handshake captured for feedback when screen not accessible'

import logging
import time
import RPi.GPIO as GPIO

OPTIONS = dict()

def on_loaded():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(OPTIONS['vPin'],GPIO.OUT)
    logging.info("vibrate plugin loaded")
    GPIO.output(OPTIONS['vPin'],GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(OPTIONS['vPin'],GPIO.LOW)

def on_handshake(agent, filename, access_point, client_station):
    logging.info("[vibrate] Got handshake - vibrating")
    GPIO.output(OPTIONS['vPin'],GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(OPTIONS['vPin'],GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(OPTIONS['vPin'],GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(OPTIONS['vPin'],GPIO.LOW)
