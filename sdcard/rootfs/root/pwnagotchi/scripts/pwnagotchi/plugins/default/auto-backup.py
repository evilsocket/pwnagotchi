__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '1.0.0'
__name__ = 'auto-backup'
__license__ = 'GPL3'
__description__ = 'This plugin backups files when internet is availaible.'

import os
import logging
import subprocess
from datetime import datetime

OPTIONS = dict()
LAST_BACKUP = None
READY = False

def on_loaded():
    """
    Gets called when the plugin gets loaded
    """
    global READY
    global LAST_BACKUP

    if 'files' not in OPTIONS or ('files' in OPTIONS and OPTIONS['files'] is None):
        logging.error("AUTO-BACKUP: No files to backup.")
        return

    if 'interval' not in OPTIONS or ('interval' in OPTIONS and OPTIONS['interval'] is None):
        logging.error("AUTO-BACKUP: Interval is not set.")
        return

    if 'commands' not in OPTIONS or ('commands' in OPTIONS and OPTIONS['commands'] is None):
        logging.error("AUTO-BACKUP: No commands given.")
        return

    if os.path.exists('/root/.auto-backup'):
        LAST_BACKUP = datetime.fromtimestamp(os.path.getmtime('/root/.auto-backup'))

    READY = True


def on_internet_available(display, config, log):
    """
    Called in manual mode when there's internet connectivity
    """
    global LAST_BACKUP

    if READY:
        if LAST_BACKUP is not None:
            if (datetime.now() - LAST_BACKUP).days < OPTIONS['interval']:
                return

        files_to_backup = " ".join(OPTIONS['files'])
        try:
            for cmd in OPTIONS['commands']:
                subprocess.call(cmd.format(files=files_to_backup).split(), stdout=open(os.devnull, 'wb'))
            logging.info("AUTO-BACKUP: Successfuly ran backup commands.")
            LAST_BACKUP = datetime.now()
            with open('/root/.auto-backup', 'w') as f:
                f.write('success')
        except OSError as os_e:
            logging.info(f"AUTO-BACKUP: Error: {os_e}")

