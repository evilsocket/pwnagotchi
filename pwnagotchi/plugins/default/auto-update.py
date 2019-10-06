__author__ = 'evilsocket@gmail.com'
__version__ = '1.0.0'
__name__ = 'auto-update'
__license__ = 'GPL3'
__description__ = 'This plugin performs an "apt update && apt upgrade" when internet is availaible.'

import logging
import subprocess
from pwnagotchi.utils import StatusFile

OPTIONS = dict()
READY = False
STATUS = StatusFile('/root/.auto-update')


def on_loaded():
    global READY

    if 'interval' not in OPTIONS or ('interval' in OPTIONS and OPTIONS['interval'] is None):
        logging.error("AUTO-UPDATE: Interval is not set.")
        return

    READY = True


def on_internet_available(display, keypair, config, log):
    global STATUS

    if READY:
        if STATUS.newer_then_days(OPTIONS['interval']):
            return

        try:
            display.set('status', 'Updating ...')
            display.update()

            logging.info("AUTO-UPDATE: updating packages index ...")

            update = subprocess.Popen('apt update -y', shell=True, stdin=None,
                                      stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
            update.wait()

            logging.info("AUTO-UPDATE: updating packages ...")

            upgrade = subprocess.Popen('apt upgrade -y', shell=True, stdin=None,
                                       stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
            upgrade.wait()

            logging.info("AUTO-UPDATE: complete.")

            STATUS.update()
        except Exception as e:
            logging.exception("AUTO-UPDATE ERROR")

        display.set('status', 'Updated!')
        display.update()
