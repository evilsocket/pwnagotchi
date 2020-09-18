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
from pwnagotchi.ui.components import LabeledValue, Text
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging


class MemTemp(plugins.Plugin):
    __author__ = 'https://github.com/xenDE'
    __version__ = '1.0.1'
    __license__ = 'GPL3'
    __description__ = 'A plugin that will display memory/cpu usage and temperature'

    def on_loaded(self):
        logging.info("memtemp plugin loaded.")

    def mem_usage(self):
        return int(pwnagotchi.mem_usage() * 100)

    def cpu_load(self):
        return int(pwnagotchi.cpu_load() * 100)

    @staticmethod
    def pad_text(width, data, symbol):
        data = str(data) + symbol
        return " " * (width - len(data)) + data

    def on_ui_setup(self, ui):
        if ui.is_waveshare_v2():
            h_pos_line1 = (178, 84)
            h_pos_line2 = (178, 94)
            v_pos_line1 = (202, 74)  # (127, 75)
            v_pos_line2 = (202, 84)  # (122, 84)
            v_pos_line3 = (197, 94)  # (127, 94)
        elif ui.is_waveshare_v1():
            h_pos_line1 = (170, 80)
            h_pos_line2 = (170, 90)
            v_pos_line1 = (170, 61)  # (130, 70)
            v_pos_line2 = (170, 71)  # (125, 80)
            v_pos_line3 = (165, 81)  # (130, 90)
        elif ui.is_waveshare144lcd():
            h_pos_line1 = (53, 77)
            h_pos_line2 = (53, 87)
            v_pos_line1 = (78, 67)  # (67, 73)
            v_pos_line2 = (78, 77)  # (62, 83)
            v_pos_line3 = (73, 87)  # (67, 93)
        elif ui.is_inky():
            h_pos_line1 = (140, 68)
            h_pos_line2 = (140, 78)
            v_pos_line1 = (165, 54)  # (127, 60)
            v_pos_line2 = (165, 64)  # (122, 70)
            v_pos_line3 = (160, 74)  # (127, 80)
        elif ui.is_waveshare27inch():
            h_pos_line1 = (192, 138)
            h_pos_line2 = (192, 148)
            v_pos_line1 = (216, 122)  # (6,120)
            v_pos_line2 = (216, 132)  # (1,135)
            v_pos_line3 = (211, 142)  # (6,150)
        else:
            h_pos_line1 = (155, 76)
            h_pos_line2 = (155, 86)
            v_pos_line1 = (180, 61)  # (127, 51)
            v_pos_line2 = (180, 71)  # (127, 56)
            v_pos_line3 = (175, 81)  # (102, 71)

        label_spacing = 0

        if self.options['orientation'] == "vertical":
            ui.add_element(
                'memtemp_line1',
                LabeledValue(
                    color=BLACK,
                    label='mem:',
                    value='-',
                    position=v_pos_line1,
                    label_font=fonts.Small,
                    text_font=fonts.Small,
                    label_spacing=label_spacing,
                )
            )
            ui.add_element(
                'memtemp_line2',
                LabeledValue(
                    color=BLACK,
                    label='cpu:',
                    value='-',
                    position=v_pos_line2,
                    label_font=fonts.Small,
                    text_font=fonts.Small,
                    label_spacing=label_spacing,
                )
            )
            ui.add_element(
                'memtemp_line3',
                LabeledValue(
                    color=BLACK,
                    label='temp:',
                    value='-',
                    position=v_pos_line3,
                    label_font=fonts.Small,
                    text_font=fonts.Small,
                    label_spacing=label_spacing,
                )
            )
        else:
            # default to horizontal
            ui.add_element(
                'memtemp_line1',
                Text(
                    color=BLACK,
                    value=' mem  cpu temp',
                    position=h_pos_line1,
                    font=fonts.Small,
                )
            )
            ui.add_element(
                'memtemp_line2',
                Text(
                    color=BLACK,
                    value='   -    -    -',
                    position=h_pos_line2,
                    font=fonts.Small,
                )
            )

    def on_unload(self, ui):
        with ui._lock:
            if self.options['orientation'] == "vertical":
                ui.remove_element('memtemp_line1')
                ui.remove_element('memtemp_line2')
                ui.remove_element('memtemp_line3')
            else:
                ui.remove_element('memtemp_line1')
                ui.remove_element('memtemp_line2')

    def on_ui_update(self, ui):
        if self.options['scale'] == "fahrenheit":
            temp = (pwnagotchi.temperature() * 9 / 5) + 32
            symbol = "f"
        elif self.options['scale'] == "kelvin":
            temp = pwnagotchi.temperature() + 273.15
            symbol = "k"
        else:
            # default to celsius
            temp = pwnagotchi.temperature()
            symbol = "c"

        if self.options['orientation'] == "vertical":
            ui.set('memtemp_line1', f"{self.mem_usage()}%")
            ui.set('memtemp_line2', f"{self.cpu_load()}%")
            ui.set('memtemp_line3', f"{temp}{symbol}")
        else:
            # default to horizontal
            ui.set(
                'memtemp_line2',
                self.pad_text(4, self.mem_usage(), "%") +
                self.pad_text(5, self.cpu_load(), "%") +
                self.pad_text(5, temp, symbol)
            )
