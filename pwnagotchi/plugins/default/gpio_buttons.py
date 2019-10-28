__author__ = 'ratmandu@gmail.com'
__version__ = '1.0.0'
__name__ = 'gpio_buttons'
__license__ = 'GPL3'
__description__ = 'GPIO Button support plugin'

import logging
import RPi.GPIO as GPIO
import subprocess

running = False
OPTIONS = dict()
GPIOs = {}
COMMANDs = None 

def runCommand(channel):
  command = GPIOs[channel]
  logging.info(f"Button Pressed! Running command: {command}")
  process = subprocess.Popen(command, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
  process.wait()


def on_loaded():
  logging.info("GPIO Button plugin loaded.")
  
  #get list of GPIOs
  gpios = OPTIONS['gpios']

  #set gpio numbering
  GPIO.setmode(GPIO.BCM)

  for i in gpios:
    gpio = list(i)[0]
    command = i[gpio]
    GPIOs[gpio] = command
    GPIO.setup(gpio, GPIO.IN, GPIO.PUD_UP)
    GPIO.add_event_detect(gpio, GPIO.FALLING, callback=runCommand, bouncetime=300)
    logging.info("Added command: %s to GPIO #%d", command, gpio)
