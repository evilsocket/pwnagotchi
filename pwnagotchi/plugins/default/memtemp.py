# tempmem shows memory infos and cpu temperature
#
# totalmem usedmem freemem cputemp
#
###############################################################
#
# Updated 18-10-2019 by spees <speeskonijn@gmail.com>
# - Changed the place where the data was displayed on screen
# - Made the data a bit more compact and easier to read
# - removed the label so we wont waste screen space
# - Updated version to 1.0.1
#
###############################################################


__author__ = 'https://github.com/xenDE'
__version__ = '1.0.1'
__name__ = 'memtemp'
__license__ = 'GPL3'
__description__ = 'A plugin that will add a memory and temperature indicator'

import struct

from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts

import time


class MEMTEMP:

    # set the minimum seconds before refresh the values
    refresh_wait = 30

    refresh_ts_last = time.time() - refresh_wait

    def __init__(self):
        # only import when the module is loaded and enabled
        import os

    def get_temp(self):
        try:
            temp = os.popen('/opt/vc/bin/vcgencmd measure_temp').readlines()[0].split('=')[1].replace("\n", '').replace("'","")
            return 't:' + temp
        except:
            return 't:-'
        # cpu:37.4C

    def get_mem_info(self):
        try:
            # includes RAM + Swap Memory:
#            total, used, free = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
            # without Swap, only real memory:
            total, used, free = map(int, os.popen('free -t -m').readlines()[-3].split()[1:4])
            return "\nT:"+str(total)+"M U:"+str(used)+"M\nF:"+str(free)+"M"
        except:
            return "\nT:-  U:-\nF:- "
        # tm:532 um:82 fm:353


memtemp = None


def on_loaded():
    global memtemp
    memtemp = MEMTEMP()


def on_ui_setup(ui):
    ui.add_element('memtemp', LabeledValue(color=BLACK, label='', value='\nT:-  U:-\nF:- -', position=(ui.width() / 2 + 17, ui.height() / 2),
                                       label_font=fonts.Bold, text_font=fonts.Medium))


def on_ui_update(ui):
    if time.time() > memtemp.refresh_ts_last + memtemp.refresh_wait:
        ui.set('memtemp', "%s %s" % (memtemp.get_mem_info(), memtemp.get_temp()))
        memtemp.refresh_ts_last = time.time()


