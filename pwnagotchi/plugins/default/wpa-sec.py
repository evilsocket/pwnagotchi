"""
This plugin automatically uploades handshakes to https://wpa-sec.stanev.org
"""

import os
import logging
import requests
from pwnagotchi.utils import StatusFile
from pwnagotchi.plugins import loaded

# Meta informations
__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '2.1.1'
__name__ = 'wpa-sec'
__license__ = 'GPL3'
__description__ = 'This plugin automatically uploades handshakes to https://wpa-sec.stanev.org'

# Variables
OPTIONS = dict()
PLUGIN = loaded[os.path.basename(__file__).replace(".py","")]


def on_loaded():
    """
    Gets called when the plugin gets loaded
    """
    PLUGIN.ready = False
    PLUGIN.skip = list()
    PLUGIN.report = StatusFile('/root/.wpa_sec_uploads', data_format='json')

    if 'api_key' not in OPTIONS or ('api_key' in OPTIONS and OPTIONS['api_key'] is None):
        logging.error("WPA_SEC: API-KEY isn't set. Can't upload to wpa-sec.stanev.org")
        return

    if 'api_url' not in OPTIONS or ('api_url' in OPTIONS and OPTIONS['api_url'] is None):
        logging.error("WPA_SEC: API-URL isn't set. Can't upload, no endpoint configured.")
        return

    if 'whitelist' not in OPTIONS:
        OPTIONS['whitelist'] = None

    PLUGIN.ready = True


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
    if PLUGIN.ready:
        config = agent.config()
        display = agent.view()
        reported = PLUGIN.report.data_field_or('reported', default=list())

        handshake_dir = config['bettercap']['handshakes']
        handshake_filenames = list()
        if OPTIONS['whitelist']:
            for filename in os.listdir(handshake_dir):
                for whity in OPTIONS['whitelist']:
                    if whity in filename:
                        break
                else:
                    # this is called if non of the whity is in the filename
                    handshake_filenames.append(filename)
        else:
            # no whitelist
            handshake_filenames = os.listdir(handshake_dir)

        handshake_paths = [os.path.join(handshake_dir, filename)
                           for filename in handshake_filenames
                           if filename.endswith('.pcap')]
        handshake_new = set(handshake_paths) - set(reported) - set(PLUGIN.skip)

        if handshake_new:
            logging.info("WPA_SEC: Internet connectivity detected. Uploading new handshakes to wpa-sec.stanev.org")

            for idx, handshake in enumerate(handshake_new):
                display.set('status', f"Uploading handshake to wpa-sec.stanev.org ({idx + 1}/{len(handshake_new)})")
                display.update(force=True)
                try:
                    _upload_to_wpasec(handshake)
                    reported.append(handshake)
                    PLUGIN.report.update(data={'reported': reported})
                    logging.info("WPA_SEC: Successfully uploaded %s", handshake)
                except requests.exceptions.RequestException as req_e:
                    PLUGIN.skip.append(handshake)
                    logging.error("WPA_SEC: %s", req_e)
                    continue
                except OSError as os_e:
                    PLUGIN.skip.append(handshake)
                    logging.error("WPA_SEC: %s", os_e)
                    continue
