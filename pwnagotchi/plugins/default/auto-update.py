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
        logging.error("auto-update: Interval is not set.")
        return

    READY = True


def run(cmd):
    return subprocess.Popen(cmd, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None,
                            executable="/bin/bash")


def on_internet_available(agent):
    global STATUS

    if READY:
        if STATUS.newer_then_days(OPTIONS['interval']):
            return

        display = agent.view()

        try:
            display.set('status', 'Updating ...')
            display.update()

            logging.info("auto-update: updating pwnagotchi ...")
            run('pip3 install --upgrade --upgrade-strategy only-if-needed pwnagotchi').wait()

            if OPTIONS['system']:
                logging.info("auto-update: updating packages index ...")
                run('apt update -y').wait()

                logging.info("auto-update: updating packages ...")
                run('apt upgrade -y').wait()

            logging.info("auto-update: complete.")
            STATUS.update()
        except Exception as e:
            logging.exception("auto-update ERROR")

        display.set('status', 'Updated!')
        display.update()
