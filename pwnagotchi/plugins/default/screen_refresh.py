__author__ = 'pwnagotcchi [at] rossmarks [dot] uk'
__version__ = '1.0.0'
__name__ = 'screen_refresh'
__license__ = 'GPL3'
__description__ = 'Refresh he e-ink display after X amount of updates'

import logging

from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts

OPTIONS = dict()
update_count = 0;

def on_loaded():
    logging.info("Screen refresh plugin loaded")

def on_ui_update(ui):
    global update_count    
    update_count += 1
    if update_count == OPTIONS['refresh_interval']:
        ui._init_display()
        ui.set('status', "Screen cleaned")
        logging.info("Screen refreshing")
        update_count = 0

