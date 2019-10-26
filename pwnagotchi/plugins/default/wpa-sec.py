__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '2.0.1'
__name__ = 'wpa-sec'
__license__ = 'GPL3'
__description__ = 'This plugin automatically uploades handshakes to https://wpa-sec.stanev.org'

import os
import logging
import requests
from pwnagotchi.utils import StatusFile

READY = False
REPORT = StatusFile('/etc/pwnagotchi/wpa_sec_uploads.json', data_format='json')
OPTIONS = dict()
SKIP = list()


def on_loaded():
    """
    Gets called when the plugin gets loaded
    """
    global READY

    if 'api_key' not in OPTIONS or ('api_key' in OPTIONS and OPTIONS['api_key'] is None):
        logging.error("WPA_SEC: API-KEY isn't set. Can't upload to wpa-sec.stanev.org")
        return

    if 'api_url' not in OPTIONS or ('api_url' in OPTIONS and OPTIONS['api_url'] is None):
        logging.error("WPA_SEC: API-URL isn't set. Can't upload, no endpoint configured.")
        return

    READY = True


def _upload_to_wpasec(path, timeout=30):
    """
    Uploads the file to https://wpa-sec.stanev.org, or another endpoint.
    """
    with open(path, 'rb') as file_to_upload:
        cookie = {'key': OPTIONS['api_key']}
        payload = {'file': file_to_upload}

        try:
            result = requests.post(OPTIONS['api_url'],
                    cookies=cookie,
                    files=payload,
                    timeout=timeout)
            if ' already submitted' in result.text:
                logging.warning("%s was already submitted.", path)
        except requests.exceptions.RequestException as req_e:
            raise req_e


def on_internet_available(agent):
    """
    Called in manual mode when there's internet connectivity
    """
    global REPORT
    global SKIP
    if READY:
        config = agent.config()
        display = agent.view()
        reported = REPORT.data_field_or('reported', default=list())

        handshake_dir = config['bettercap']['handshakes']
        handshake_filenames = os.listdir(handshake_dir)
        handshake_paths = [os.path.join(handshake_dir, filename) for filename in handshake_filenames if filename.endswith('.pcap')]
        handshake_new = set(handshake_paths) - set(reported) - set(SKIP)

        if handshake_new:
            logging.info("WPA_SEC: Internet connectivity detected. Uploading new handshakes to wpa-sec.stanev.org")

            for idx, handshake in enumerate(handshake_new):
                display.set('status', f"Uploading handshake to wpa-sec.stanev.org ({idx + 1}/{len(handshake_new)})")
                display.update(force=True)
                try:
                    _upload_to_wpasec(handshake)
                    reported.append(handshake)
                    REPORT.update(data={'reported': reported})
                    logging.info("WPA_SEC: Successfuly uploaded %s", handshake)
                except requests.exceptions.RequestException as req_e:
                    SKIP.append(handshake)
                    logging.error("WPA_SEC: %s", req_e)
                    continue
                except OSError as os_e:
                    logging.error("WPA_SEC: %s", os_e)
                    continue
