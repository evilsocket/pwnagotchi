# memtemp shows memory infos and cpu temperature
#
# mem usage, cpu load, cpu temp, cpu frequency
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
# 19-09-2020 by crahan <crahan@n00.be>
# - Added CPU frequency
# - Made field types and order configurable (max 3 fields)
# - Made line spacing and position configurable
# - Updated code to dynamically generate UI elements
# - Changed horizontal UI elements to Text
# - Updated to version 1.0.2
###############################################################
from pwnagotchi.ui.components import LabeledValue, Text
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging


class MemTemp(plugins.Plugin):
    __author__ = 'https://github.com/xenDE'
    __version__ = '1.0.2'
    __license__ = 'GPL3'
    __description__ = 'A plugin that will display memory/cpu usage and temperature'

    ALLOWED_FIELDS = {
        'mem': 'mem_usage',
        'cpu': 'cpu_load',
        'temp': 'cpu_temp',
        'freq': 'cpu_freq'
    }
    DEFAULT_FIELDS = ['mem', 'cpu', 'temp']
    LINE_SPACING = 10
    LABEL_SPACING = 0
    FIELD_WIDTH = 4

    def on_loaded(self):
        logging.info("memtemp plugin loaded.")

    def mem_usage(self):
        return f"{int(pwnagotchi.mem_usage() * 100)}%"

    def cpu_load(self):
        return f"{int(pwnagotchi.cpu_load() * 100)}%"

    def cpu_temp(self):
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
        return f"{temp}{symbol}"

    def cpu_freq(self):
        with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq', 'rt') as fp:
            return f"{round(float(fp.readline())/1000000, 1)}G"

    def pad_text(self, data):
        return " " * (self.FIELD_WIDTH - len(data)) + data

    def on_ui_setup(self, ui):
        try:
            # Configure field list
            self.fields = self.options['fields'].split(',')
            self.fields = [x.strip() for x in self.fields if x.strip() in self.ALLOWED_FIELDS.keys()]
            self.fields = self.fields[:3]  # limit to the first 3 fields
        except Exception:
            # Set default value
            self.fields = self.DEFAULT_FIELDS

        try:
            # Configure line_spacing
            line_spacing = int(self.options['linespacing'])
        except Exception:
            # Set default value
            line_spacing = self.LINE_SPACING

        try:
            # Configure position
            pos = self.options['position'].split(',')
            pos = [int(x.strip()) for x in pos]
            if self.options['orientation'] == "vertical":
                v_pos = (pos[0], pos[1])
            else:
                h_pos = (pos[0], pos[1])
        except Exception:
            # Set default position based on screen type
            if ui.is_waveshare_v2():
                h_pos = (178, 84)
                v_pos = (197, 74)
            elif ui.is_waveshare_v1():
                h_pos = (170, 80)
                v_pos = (165, 61)
            elif ui.is_waveshare144lcd():
                h_pos = (53, 77)
                v_pos = (73, 67)
            elif ui.is_inky():
                h_pos = (140, 68)
                v_pos = (160, 54)
            elif ui.is_waveshare27inch():
                h_pos = (192, 138)
                v_pos = (211, 122)
            else:
                h_pos = (155, 76)
                v_pos = (175, 61)

        if self.options['orientation'] == "vertical":
            # Dynamically create the required LabeledValue objects
            for idx, field in enumerate(self.fields):
                v_pos_x = v_pos[0]
                v_pos_y = v_pos[1] + ((len(self.fields) - 3) * -1 * line_spacing)
                ui.add_element(
                    f"memtemp_{field}",
                    LabeledValue(
                        color=BLACK,
                        label=f"{self.pad_text(field)}:",
                        value="-",
                        position=(v_pos_x, v_pos_y + (idx * line_spacing)),
                        label_font=fonts.Small,
                        text_font=fonts.Small,
                        label_spacing=self.LABEL_SPACING,
                    )
                )
        else:
            # default to horizontal
            h_pos_x = h_pos[0] + ((len(self.fields) - 3) * -1 * 25)
            h_pos_y = h_pos[1]
            ui.add_element(
                'memtemp_header',
                Text(
                    color=BLACK,
                    value=" ".join([self.pad_text(x) for x in self.fields]),
                    position=(h_pos_x, h_pos_y),
                    font=fonts.Small,
                )
            )
            ui.add_element(
                'memtemp_data',
                Text(
                    color=BLACK,
                    value=" ".join([self.pad_text("-") for x in self.fields]),
                    position=(h_pos_x, h_pos_y + line_spacing),
                    font=fonts.Small,
                )
            )

    def on_unload(self, ui):
        with ui._lock:
            if self.options['orientation'] == "vertical":
                for idx, field in enumerate(self.fields):
                    ui.remove_element(f"memtemp_{field}")
            else:
                # default to horizontal
                ui.remove_element('memtemp_header')
                ui.remove_element('memtemp_data')

    def on_ui_update(self, ui):
        if self.options['orientation'] == "vertical":
            for idx, field in enumerate(self.fields):
                ui.set(f"memtemp_{field}", getattr(self, self.ALLOWED_FIELDS[field])())
        else:
            # default to horizontal
            data = " ".join([self.pad_text(getattr(self, self.ALLOWED_FIELDS[x])()) for x in self.fields])
            ui.set('memtemp_data', data)
