import os
import logging
import re
import subprocess
from io import TextIOWrapper
from time import sleep
from threading import Lock
from pwnagotchi import plugins


class Watchdog(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '0.1.0'
    __license__ = 'GPL3'
    __description__ = 'Restart pwnagotchi when blindbug is detected.'

    def __init__(self):
        self.options = dict()
        self.lock = Lock()
        self.pattern = re.compile(r'brcmf_cfg80211_nexmon_set_channel.*?Set Channel failed')

    def on_loaded(self):
        """
        Gets called when the plugin gets loaded
        """
        logging.info("Watchdog plugin loaded.")

    def on_epoch(self, agent, epoch, epoch_data):
        if self.lock.locked():
            return
        with self.lock:
            # get last 10 lines
            last_lines = ''.join(list(TextIOWrapper(subprocess.Popen(['journalctl','-n10','-k'],
                                                  stdout=subprocess.PIPE).stdout))[-10:])
            if len(self.pattern.findall(last_lines)) >= 3:
                display = agent.view()
                display.set('status', 'Blind-Bug detected. Restarting bettercap.')
                display.update(force=True)
                logging.info('[WATCHDOG] Blind-Bug detected. Restarting.')
                mode_file = '/root/.pwnagotchi-manual' if agent.mode == 'manual' else '/root/.pwnagotchi-auto'
                os.system(f"touch {mode_file}")
                os.system('systemctl restart bettercap')
                sleep(10)