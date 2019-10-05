__author__ = 'evilsocket@gmail.com'
__version__ = '1.0.0'
__name__ = 'auto-update'
__license__ = 'GPL3'
__description__ = 'This plugin performs an "apt update && apt upgrade" when internet is availaible.'

import os
import logging
import subprocess
from datetime import datetime

OPTIONS = dict()
LAST_UPDATE = None
READY = False
STATUS_FILE = '/root/.auto-update'


def on_loaded():
    global READY
    global LAST_UPDATE

    if 'interval' not in OPTIONS or ('interval' in OPTIONS and OPTIONS['interval'] is None):
        logging.error("AUTO-UPDATE: Interval is not set.")
        return

    if os.path.exists(STATUS_FILE):
        LAST_UPDATE = datetime.fromtimestamp(os.path.getmtime(STATUS_FILE))

    READY = True


def on_internet_available(display, config, log):
    global LAST_UPDATE

    if READY:
        if LAST_UPDATE is not None:
            if (datetime.now() - LAST_UPDATE).days < OPTIONS['interval']:
                return

        try:
            logging.info("AUTO-UPDATE: updating packages index ...")

            update = subprocess.Popen('apt update -y', shell=True, stdin=None,
                                      stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
            update.wait()

            logging.info("AUTO-UPDATE: updating packages ...")

            upgrade = subprocess.Popen('apt upgrade -y', shell=True, stdin=None,
                                       stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
            upgrade.wait()

            logging.info("AUTO-UPDATE: complete.")

            LAST_UPDATE = datetime.now()
            with open(STATUS_FILE, 'w') as f:
                f.write('success')
        except Exception as e:
            logging.exception("AUTO-UPDATE ERROR")
