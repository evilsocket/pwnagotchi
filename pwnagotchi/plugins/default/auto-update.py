__author__ = 'evilsocket@gmail.com'
__version__ = '1.1.0'
__name__ = 'auto-update'
__license__ = 'GPL3'
__description__ = 'This plugin checks when updates are available and applies them when internet is available.'

import logging
import subprocess
from pwnagotchi.utils import StatusFile

OPTIONS = dict()
READY = False
STATUS = StatusFile('/root/.auto-update')


def on_loaded():
    global READY
    if 'interval' not in OPTIONS or ('interval' in OPTIONS and OPTIONS['interval'] is None):
        logging.error("[update] main.plugins.auto-update.interval is not set")
        return
    READY = True
    logging.info("[update] plugin loaded.")


def run(cmd):
    return subprocess.Popen(cmd, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None,
                            executable="/bin/bash")


def on_internet_available(agent):
    global STATUS

    if READY:
        if STATUS.newer_then_hours(OPTIONS['interval']):
            logging.debug("[update] last check happened less than %d hours ago" % OPTIONS['interval'])
            return

        logging.debug("[update] start")

        display = agent.view()
        prev_status = display.get('status')

        try:
            display.set('status', 'Checking for updates ...')
            display.update()

            """
            logging.info("auto-update: updating pwnagotchi ...")
            run('pip3 install --upgrade --upgrade-strategy only-if-needed pwnagotchi').wait()

            if OPTIONS['system']:
                logging.info("auto-update: updating packages index ...")
                run('apt update -y').wait()

                logging.info("auto-update: updating packages ...")
                run('apt upgrade -y').wait()
            """

            logging.info("[update] done")

            STATUS.update()

        except Exception as e:
            logging.error("[update] %s" % e)

        display.set('status', prev_status if prev_status is not None else '')
        display.update()
