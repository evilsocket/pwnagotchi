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
        self.tries = 0
        self.status = StatusFile('/root/.auto-backup')

    def on_loaded(self):
        for opt in ['files', 'interval', 'commands', 'max_tries']:
            if opt not in self.options or (opt in self.options and self.options[opt] is None):
                logging.error(f"AUTO-BACKUP: Option {opt} is not set.")
                return

        self.ready = True
        logging.info("AUTO-BACKUP: Successfully loaded.")

    def on_internet_available(self, agent):
        if not self.ready:
            return

        if self.options['max_tries'] and self.tries >= self.options['max_tries']:
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
            self.tries += 1
            logging.info(f"AUTO-BACKUP: Error: {os_e}")
            display.set('status', 'Backup failed!')
            display.update()
