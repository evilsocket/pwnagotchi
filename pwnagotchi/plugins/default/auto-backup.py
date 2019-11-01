import pwnagotchi.plugins as plugins
from pwnagotchi.utils import StatusFile
import logging
import os
import subprocess


class AutoBackup(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'This plugin backups files when internet is available.'

    def __init__(self):
        self.ready = False
        self.status = StatusFile('/root/.auto-backup')

    def on_loaded(self):
        if 'files' not in self.options or ('files' in self.options and self.options['files'] is None):
            logging.error("AUTO-BACKUP: No files to backup.")
            return

        if 'interval' not in self.options or ('interval' in self.options and self.options['interval'] is None):
            logging.error("AUTO-BACKUP: Interval is not set.")
            return

        if 'commands' not in self.options or ('commands' in self.options and self.options['commands'] is None):
            logging.error("AUTO-BACKUP: No commands given.")
            return

        self.ready = True
        logging.info("AUTO-BACKUP: Successfully loaded.")

    def on_internet_available(self, agent):
        if not self.ready:
            return

        if self.status.newer_then_days(self.options['interval']):
            return

        # Only backup existing files to prevent errors
        existing_files = list(filter(lambda f: os.path.exists(f), self.options['files']))
        files_to_backup = " ".join(existing_files)

        try:
            display = agent.view()

            logging.info("AUTO-BACKUP: Backing up ...")
            display.set('status', 'Backing up ...')
            display.update()

            for cmd in self.options['commands']:
                logging.info(f"AUTO-BACKUP: Running {cmd.format(files=files_to_backup)}")
                process = subprocess.Popen(cmd.format(files=files_to_backup), shell=True, stdin=None,
                                           stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
                process.wait()
                if process.returncode > 0:
                    raise OSError(f"Command failed (rc: {process.returncode})")

            logging.info("AUTO-BACKUP: backup done")
            display.set('status', 'Backup done!')
            display.update()
            self.status.update()
        except OSError as os_e:
            logging.info(f"AUTO-BACKUP: Error: {os_e}")
            display.set('status', 'Backup failed!')
            display.update()
