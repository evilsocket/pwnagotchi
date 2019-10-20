# memtemp shows memory infos and cpu temperature
#
# mem usage, cpu load, cpu temp
#
###############################################################
#
# Updated 18-10-2019 by spees <speeskonijn@gmail.com>
# - Changed the place where the data was displayed on screen
# - Made the data a bit more compact and easier to read
# - removed the label so we wont waste screen space
# - Updated version to 1.0.1
#
# 20-10-2019 by spees <speeskonijn@gmail.com>
# - Refactored to use the already existing functions
# - Now only shows memory usage in percentage
# - Added CPU load
# - Added horizontal and vertical orientation
#
###############################################################

__author__ = 'https://github.com/xenDE'
__version__ = '1.0.1'
__name__ = 'memtemp'
__license__ = 'GPL3'
__description__ = 'A plugin that will display memory/cpu usage and temperature'


from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi
import subprocess
import logging

OPTIONS = dict()


def on_loaded():
    logging.info("memtemp plugin loaded.")


def mem_usage():
    return int(pwnagotchi.mem_usage() * 100)

def cpu_load():
    return int(pwnagotchi.cpu_load() * 100)



def on_ui_setup(ui):
    if OPTIONS['orientation'] == "horizontal":
        ui.add_element('memtemp', LabeledValue(color=BLACK, label='', value='mem cpu temp\n - -  -', position=(ui.width() / 2 + 30, ui.height() /2 + 15),
                                        label_font=fonts.Small, text_font=fonts.Small))
    elif OPTIONS['orientation'] == "vertical":
        ui.add_element('memtemp', LabeledValue(color=BLACK, label='', value=' mem:-\n cpu:-\ntemp:-', position=(ui.width() / 2 + 55, ui.height() /2),
                                        label_font=fonts.Small, text_font=fonts.Small))

def on_ui_update(ui):
    if OPTIONS['orientation'] == "horizontal":
        ui.set('memtemp', " mem cpu temp\n %s%% %s%%  %sc" % (mem_usage(), cpu_load(), pwnagotchi.temperature()))
    
    elif OPTIONS['orientation'] == "vertical":
        ui.set('memtemp', " mem:%s%%\n cpu:%s%%\ntemp:%sc" % (mem_usage(), cpu_load(), pwnagotchi.temperature()))
