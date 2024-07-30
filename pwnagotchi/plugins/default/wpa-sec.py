import os
import re
import logging
import requests
from datetime import datetime
from threading import Lock
from pwnagotchi.utils import StatusFile, remove_whitelisted
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
        except JSONDecodeError:
            os.remove("/root/.wpa_sec_uploads")
            self.report = StatusFile('/root/.wpa_sec_uploads', data_format='json')
        self.options = dict()
        self.skip = list()

    def _upload_to_wpasec(self, path, timeout=30):
        """
        Uploads the file to wpasec
        """
        with open(path, 'rb') as file_to_upload:
            cookie = {'key': self.options['api_key']}
            payload = {'file': file_to_upload}

            logging.info("WPA_SEC: Uploading %s...", path)

            result = requests.post(self.options['api_url'],
                                cookies=cookie,
                                files=payload,
                                timeout=timeout)
            result.raise_for_status()
            
            logging.info("WPA_SEC: Uploaded %s. Response was: %s.", path, result.text.partition('\n')[0])

    def _download_from_wpasec(self, output, timeout=30):
        """
        Downloads the results from wpasec and saves them to output

        Output-Format: bssid, station_mac, ssid, password
        """
        api_url = self.options['api_url']
        if not api_url.endswith('/'):
            api_url = f"{api_url}/"
        api_url = f"{api_url}?api&dl=1"

        cookie = {'key': self.options['api_key']}

        logging.info("WPA_SEC: Downloading cracked passwords...")

        result = requests.get(api_url, cookies=cookie, timeout=timeout)
        result.raise_for_status()

        with open(output, 'wb') as output_file:
            output_file.write(result.content)

        logging.info("WPA_SEC: Downloaded cracked passwords.")

    def _write_cracked_single_files(self, cracked_file_path, handshake_dir):
        """
        Splits download results from wpasec into individual .pcap..cracked files in handshake_dir

        Each .pcap.cracked file will contain the cracked handshake password
        """
        logging.info("WPA_SEC: Writing cracked single files...")

        with open(cracked_file_path, 'r') as cracked_file:
            for line in cracked_file:
                try:
                    bssid,station_mac,ssid,password = line.split(":")
                    if password:
                        filename = re.sub(r'[^a-zA-Z0-9]', '', ssid) + '_' + bssid
                        if os.path.exists( os.path.join(handshake_dir, filename+'.pcap') ) and not os.path.exists( os.path.join(handshake_dir, filename+'.pcap.cracked') ):
                            with open(os.path.join(handshake_dir, filename+'.pcap.cracked'), 'w') as f:
                                f.write(password)
                except Exception:
                    logging.exception(f"WPA_SEC: Exception writing cracked single file, parsing line {line}.")
    
        logging.info("WPA_SEC: Wrote cracked single files.")

    def on_loaded(self):
        """
        Gets called when the plugin gets loaded
        """
        if 'api_key' not in self.options or ('api_key' in self.options and not self.options['api_key']):
            logging.error("WPA_SEC: API-KEY isn't set. Can't upload.")
            return

        if 'api_url' not in self.options or ('api_url' in self.options and not self.options['api_url']):
            logging.error("WPA_SEC: API-URL isn't set. Can't upload.")
            return

        if 'whitelist' not in self.options:
            self.options['whitelist'] = list()

        self.ready = True
        logging.info("WPA_SEC: plugin loaded.")

    def on_webhook(self, path, request):
        from flask import make_response, redirect
        response = make_response(redirect(self.options['api_url'], code=302))
        response.set_cookie('key', self.options['api_key'])
        return response

    def on_internet_available(self, agent):
        """
        Called in manual mode when there's internet connectivity
        """
        if not self.ready or self.lock.locked():
            return

        with self.lock:
            config = agent.config()
            display = agent.view()
            reported = self.report.data_field_or('reported', default=list())
            handshake_dir = config['bettercap']['handshakes']
            handshake_filenames = os.listdir(handshake_dir)
            handshake_paths = [os.path.join(handshake_dir, filename) for filename in handshake_filenames if
                               filename.endswith('.pcap')]
            handshake_paths = remove_whitelisted(handshake_paths, self.options['whitelist'])
            handshake_new = set(handshake_paths) - set(reported) - set(self.skip)

            if handshake_new:
                logging.info("WPA_SEC: Internet connectivity detected. Uploading new handshakes...")
                for idx, handshake in enumerate(handshake_new):
                    display.on_uploading(f"WPA-SEC ({idx + 1}/{len(handshake_new)})")

                    try:
                        self._upload_to_wpasec(handshake)
                        reported.append(handshake)
                        self.report.update(data={'reported': reported})
                    except requests.exceptions.RequestException:
                        self.skip.append(handshake)
                        logging.exception("WPA_SEC: RequestException uploading %s.", handshake)
                    except Exception:
                        logging.exception("WPA_SEC: Exception uploading %s.", handshake)

                display.on_normal()

            if 'download_results' in self.options and self.options['download_results']:
                cracked_file_path = os.path.join(handshake_dir, 'wpa-sec.cracked.potfile')

                if os.path.exists(cracked_file_path):
                    last_check = datetime.fromtimestamp(os.path.getmtime(cracked_file_path))
                    download_interval = int(self.options.get('download_interval', 3600))
                    if last_check is not None and ((datetime.now() - last_check).seconds / download_interval) < 1:
                        return

                try:
                    self._download_from_wpasec(cracked_file_path)
                    if 'single_files' in self.options and self.options['single_files']:
                        self._write_cracked_single_files(cracked_file_path, handshake_dir)
                except Exception:
                    logging.exception("WPA_SEC: Exception downloading results.")
