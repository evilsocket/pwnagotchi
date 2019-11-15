import json
import logging
import os

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class GPS(plugins.Plugin):
    __author__ = "evilsocket@gmail.com"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Save GPS coordinates whenever an handshake is captured."

    def __init__(self):
        self.running = False
        self.coordinates = None

    def on_loaded(self):
        logging.info(f"gps plugin loaded for {self.options['device']}")

    def on_ready(self, agent):
        if os.path.exists(self.options["device"]):
            logging.info(
                f"enabling bettercap's gps module for {self.options['device']}"
            )
            try:
                agent.run("gps off")
            except Exception:
                pass

            agent.run(f"set gps.device {self.options['device']}")
            agent.run(f"set gps.baudrate {self.options['speed']}")
            agent.run("gps on")
            self.running = True
        else:
            logging.warning("no GPS detected")

    def on_handshake(self, agent, filename, access_point, client_station):
        if self.running:
            info = agent.session()
            self.coordinates = info["gps"]
            gps_filename = filename.replace(".pcap", ".gps.json")

            logging.info(f"saving GPS to {gps_filename} ({self.coordinates})")
            with open(gps_filename, "w+t") as fp:
                json.dump(self.coordinates, fp)

    def on_ui_setup(self, ui):
        # add coordinates for other displays
        if ui.is_waveshare_v2():
            lat_pos = (127, 75)
            lon_pos = (122, 84)
            alt_pos = (127, 94)
        elif ui.is_inky():
            # guessed values, add tested ones if you can
            lat_pos = (112, 30)
            lon_pos = (112, 49)
            alt_pos = (87, 63)
        else:
            # guessed values, add tested ones if you can
            lat_pos = (127, 51)
            lon_pos = (127, 56)
            alt_pos = (102, 71)

        label_spacing = 0

        ui.add_element(
            "latitude",
            LabeledValue(
                color=BLACK,
                label="lat:",
                value="-",
                position=lat_pos,
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=label_spacing,
            ),
        )
        ui.add_element(
            "longitude",
            LabeledValue(
                color=BLACK,
                label="long:",
                value="-",
                position=lon_pos,
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=label_spacing,
            ),
        )
        ui.add_element(
            "altitude",
            LabeledValue(
                color=BLACK,
                label="alt:",
                value="-",
                position=alt_pos,
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=label_spacing,
            ),
        )

    def on_ui_update(self, ui):
        if self.coordinates and all([
            # avoid 0.000... measurements
            self.coordinates["Latitude"], self.coordinates["Longitude"]
        ]):
            # last char is sometimes not completely drawn ¯\_(ツ)_/¯
            # using an ending-whitespace as workaround on each line
            ui.set("latitude", f"{self.coordinates['Latitude']:.4f} ")
            ui.set("longitude", f" {self.coordinates['Longitude']:.4f} ")
            ui.set("altitude", f" {self.coordinates['Altitude']:.1f}m ")
