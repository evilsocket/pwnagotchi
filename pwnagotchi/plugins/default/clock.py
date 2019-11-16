import logging
import re
import subprocess
from datetime import datetime
from time import ctime
from subprocess import CalledProcessError

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
from socket import socket, AF_INET, SOCK_DGRAM
import struct


class Clock(plugins.Plugin):
    __author__ = "benleb"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __plugin__ = "clock"
    __description__ = "Shows the time, sometimes even the current one."

    def __init__(self):
        self.synced = False

    def timedatectl_state(self):
        try:
            state = subprocess.run(
                ["timedatectl", "status"],
                capture_output=True, check=True, text=True, timeout=5
            )

            matches = re.search(r".*System clock synchronized: (\w*)\W", state.stdout, re.MULTILINE)
            if matches and matches.group(1) == "yes":
                logging.info(f"[{self.__plugin__}]: system clock is in sync")
                self.synced = True

            return self.synced

        except TimeoutError as error:
            logging.error(f"[{self.__plugin__}] timeout: {error}")
        except CalledProcessError as error:
            logging.error(f"[{self.__plugin__}] error: {error}")

    def on_loaded(self):
        logging.info(f"[{self.__plugin__}]: plugin loaded")

    def on_ready(self, agent):
        self.timedatectl_state()
        # try:
        #     state = subprocess.run(
        #         ["timedatectl", "status"],
        #         capture_output=True, check=True, text=True, timeout=5
        #     )

        #     matches = re.search(r".*System clock synchronized: (\w*)\W", state.stdout, re.MULTILINE)
        #     if matches and matches.group(1) == "yes":
        #         logging.info(f"[{self.__plugin__}]: system clock is synchronized")
        #         self.synced = True

        # except TimeoutError as error:
        #     logging.error(f"[{self.__plugin__}] timeout: {error}")
        # except CalledProcessError as error:
        #     logging.error(f"[{self.__plugin__}] error: {error}")

    def on_ui_setup(self, ui):
        if ui.is_waveshare_v2():
            pos = (208, 67)
        elif ui.is_inky():
            # guessed values, add tested ones if you can
            pos = (112, 30)
        else:
            # guessed values, add tested ones if you can
            pos = (127, 51)

        label_spacing = 0

        ui.add_element(
            "clock",
            LabeledValue(
                color=BLACK,
                label="",
                value="-:-:-",
                position=pos,
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=label_spacing,
            ),
        )

        if self.synced:
            ui.set("clock", f"{datetime.now().time().isoformat(timespec='seconds')} ")
        elif self.query_ntp():
            ui.set("clock", f"{self.query_ntp()} ")

    def on_ui_update(self, ui):
        if self.synced:
            ui.set("clock", f"{datetime.now().time().isoformat(timespec='seconds')} ")
        else:
            ui.set("clock", f"-:-:- ")

    def on_wait(self, agent, t):
        if not self.synced:
            self.query_ntp()

    def on_bored(self, agent):
        if not self.synced:
            self.query_ntp()

    def on_internet_available(self, agent):
        self.timedatectl_state()

        if not self.synced:
            self.query_ntp()

    def query_ntp(self):
        host = "pool.ntp.org"
        port = 123
        address = (host, port)
        msg = b"\x1b" + 47 * b"\0"
        buf = 1024

        logging.debug(f"[{self.__plugin__}]: syncing clock with {host}")

        # reference time (in seconds since 1900-01-01 00:00:00)
        TIME1970 = 2208988800

        # connect to server
        client = socket(AF_INET, SOCK_DGRAM)
        try:
            client.sendto(msg, address)
            msg, address = client.recvfrom(buf)
        except Exception as error:
            logging.error(f"[{self.__plugin__}] error: {error}")
        finally:
            client.close()

        t = struct.unpack("!12I", msg)[10]
        t -= TIME1970

        matches = re.search(r".* (\d{2}:\d{2}:\d{2}) .*", ctime(t))
        ntp_time = matches.group(1)

        logging.debug(f"[{self.__plugin__}]: synchronized clock with {host} - {ntp_time}")

        return ntp_time
