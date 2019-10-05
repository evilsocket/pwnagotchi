__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '1.0.0'
__name__ = 'auto-backup'
__license__ = 'GPL3'
__description__ = 'This plugin backups files when internet is availaible.'

from pwnagotchi.utils import StatusFile
import logging
import os
import subprocess

OPTIONS = dict()
READY = False
STATUS = StatusFile('/root/.auto-backup')


def on_loaded():
    global READY

    if 'files' not in OPTIONS or ('files' in OPTIONS and OPTIONS['files'] is None):
        logging.error("AUTO-BACKUP: No files to backup.")
        return

    if 'interval' not in OPTIONS or ('interval' in OPTIONS and OPTIONS['interval'] is None):
        logging.error("AUTO-BACKUP: Interval is not set.")
        return

    if 'commands' not in OPTIONS or ('commands' in OPTIONS and OPTIONS['commands'] is None):
        logging.error("AUTO-BACKUP: No commands given.")
        return

    READY = True


def on_internet_available(display, config, log):
    global STATUS

    if READY:
        if STATUS.newer_then_days(OPTIONS['interval']):
            return

        files_to_backup = " ".join(OPTIONS['files'])
        try:
            display.set('status', 'Backing up ...')
            display.update()

            for cmd in OPTIONS['commands']:
                subprocess.call(cmd.format(files=files_to_backup).split(), stdout=open(os.devnull, 'wb'))

            logging.info("AUTO-BACKUP: backup done")
            STATUS.update()
        except OSError as os_e:
            logging.info(f"AUTO-BACKUP: Error: {os_e}")

        display.set('status', 'Backup done!')
        display.update()
