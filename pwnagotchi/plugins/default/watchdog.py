import os
import logging
import re
import subprocess
from io import TextIOWrapper
from pwnagotchi import plugins


class Watchdog(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '0.1.0'
    __license__ = 'GPL3'
    __description__ = 'Restart pwnagotchi when blindbug is detected.'

    def __init__(self):
        self.options = dict()
        self.pattern = re.compile(r'brcmf_cfg80211_nexmon_set_channel.*?Set Channel failed')

    def on_loaded(self):
        """
        Gets called when the plugin gets loaded
        """
        logging.info("Watchdog plugin loaded.")

    def on_epoch(self, agent, epoch, epoch_data):
        # get last 10 lines
        last_lines = ''.join(list(TextIOWrapper(subprocess.Popen(['journalctl','-n10','-k', '--since', '-5m'],
                                                stdout=subprocess.PIPE).stdout))[-10:])
        if len(self.pattern.findall(last_lines)) >= 5:
            display = agent.view()
            display.set('status', 'Blind-Bug detected. Restarting.')
            display.update(force=True)
            logging.info('[WATCHDOG] Blind-Bug detected. Restarting.')
            mode = 'MANU' if agent.mode == 'manual' else 'AUTO'
            import pwnagotchi
            pwnagotchi.reboot(mode=mode)
