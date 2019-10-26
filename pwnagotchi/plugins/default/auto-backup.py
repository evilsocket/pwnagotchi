"""
Auto-Backup plugin
"""
import logging
import os
import subprocess
from pwnagotchi.utils import StatusFile
from pwnagotchi.plugins import loaded

# Meta informations
__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '1.0.0'
__name__ = 'auto-backup'
__license__ = 'GPL3'
__description__ = 'This plugin backups files when internet is available.'

# Variables
OPTIONS = dict()
PLUGIN = loaded[os.path.basename(__file__).replace(".py","")]


def on_loaded():
    PLUGIN.ready = False
    PLUGIN.status = StatusFile('/root/.auto-backup')

    if 'files' not in OPTIONS or ('files' in OPTIONS and OPTIONS['files'] is None):
        logging.error("AUTO-BACKUP: No files to backup.")
        return

    if 'interval' not in OPTIONS or ('interval' in OPTIONS and OPTIONS['interval'] is None):
        logging.error("AUTO-BACKUP: Interval is not set.")
        return

    if 'commands' not in OPTIONS or ('commands' in OPTIONS and OPTIONS['commands'] is None):
        logging.error("AUTO-BACKUP: No commands given.")
        return

    PLUGIN.ready = True
    logging.info("AUTO-BACKUP: Successfully loaded.")


def on_internet_available(agent):
    if PLUGIN.ready:
        if PLUGIN.status.newer_then_days(OPTIONS['interval']):
            return

        # Only backup existing files to prevent errors
        existing_files = list(filter(lambda f: os.path.exists(f), OPTIONS['files']))
        files_to_backup = " ".join(existing_files)

        try:
            display = agent.view()

            logging.info("AUTO-BACKUP: Backing up ...")
            display.set('status', 'Backing up ...')
            display.update()

            for cmd in OPTIONS['commands']:
                logging.info(f"AUTO-BACKUP: Running {cmd.format(files=files_to_backup)}")
                process = subprocess.Popen(cmd.format(files=files_to_backup), shell=True, stdin=None,
                                          stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
                process.wait()
                if process.returncode > 0:
                    raise OSError(f"Command failed (rc: {process.returncode})")

            logging.info("AUTO-BACKUP: backup done")
            display.set('status', 'Backup done!')
            display.update()
            PLUGIN.status.update()
        except OSError as os_e:
            logging.info("AUTO-BACKUP: %s", os_e)
            display.set('status', 'Backup failed!')
            display.update()
