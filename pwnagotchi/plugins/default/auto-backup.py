__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '1.0.0'
__name__ = 'auto-backup'
__license__ = 'GPL3'
__description__ = 'This plugin backups files when internet is available.'

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
    logging.info("AUTO-BACKUP: Successfuly loaded.")


def on_internet_available(agent):
    global STATUS

    if READY:
        if STATUS.newer_then_days(OPTIONS['interval']):
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
            STATUS.update()
        except OSError as os_e:
            logging.info(f"AUTO-BACKUP: Error: {os_e}")
            display.set('status', 'Backup failed!')
            display.update()
