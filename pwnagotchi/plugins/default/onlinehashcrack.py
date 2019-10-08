__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '1.0.0'
__name__ = 'onlinehashcrack'
__license__ = 'GPL3'
__description__ = 'This plugin automatically uploades handshakes to https://onlinehashcrack.com'

import os
import logging
import requests

READY = False
ALREADY_UPLOADED = None
OPTIONS = dict()


def on_loaded():
    """
    Gets called when the plugin gets loaded
    """
    global READY
    global EMAIL
    global ALREADY_UPLOADED

    if not 'email' in OPTIONS or ('email' in OPTIONS and OPTIONS['email'] is None):
        logging.error("OHC: Email isn't set. Can't upload to onlinehashcrack.com")
        return

    try:
        with open('/root/.ohc_uploads', 'r') as f:
            ALREADY_UPLOADED = f.read().splitlines()
    except OSError:
        logging.warning('OHC: No upload-file found.')
        ALREADY_UPLOADED = []

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


def on_internet_available(display, keypair, config, log):
    """
    Called in manual mode when there's internet connectivity
    """
    if READY:
        handshake_dir = config['bettercap']['handshakes']
        handshake_filenames = os.listdir(handshake_dir)
        handshake_paths = [os.path.join(handshake_dir, filename) for filename in handshake_filenames if filename.endswith('.pcap')]
        handshake_new = set(handshake_paths) - set(ALREADY_UPLOADED)

        if handshake_new:
            logging.info("OHC: Internet connectivity detected. Uploading new handshakes to onelinehashcrack.com")

            for idx, handshake in enumerate(handshake_new):
                display.set('status', f"Uploading handshake to onlinehashcrack.com ({idx + 1}/{len(handshake_new)})")
                display.update(force=True)
                try:
                    _upload_to_ohc(handshake)
                    ALREADY_UPLOADED.append(handshake)
                    with open('/root/.ohc_uploads', 'a') as f:
                        f.write(handshake + "\n")
                    logging.info(f"OHC: Successfuly uploaded {handshake}")
                except requests.exceptions.RequestException:
                    pass
                except OSError as os_e:
                    logging.error(f"OHC: Got the following error: {os_e}")

