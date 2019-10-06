__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '1.0.0'
__name__ = 'wpa-sec'
__license__ = 'GPL3'
__description__ = 'This plugin automatically uploades handshakes to https://wpa-sec.stanev.org'

import os
import logging
import requests

READY = False
ALREADY_UPLOADED = None


def on_loaded():
    """
    Gets called when the plugin gets loaded
    """
    global READY
    global API_KEY
    global ALREADY_UPLOADED

    if not 'api_key' in OPTIONS or ('api_key' in OPTIONS and OPTIONS['api_key'] is None):
        logging.error("WPA_SEC: API-KEY isn't set. Can't upload to wpa-sec.stanev.org")
        return

    try:
        with open('/root/.wpa_sec_uploads', 'r') as f:
            ALREADY_UPLOADED = f.read().splitlines()
    except OSError:
        logging.warning('WPA_SEC: No upload-file found.')
        ALREADY_UPLOADED = []

    READY = True


def _upload_to_wpasec(path, timeout=30):
    """
    Uploads the file to wpa-sec.stanev.org
    """
    with open(path, 'rb') as file_to_upload:
        headers = {'key': OPTIONS['api_key']}
        payload = {'file': file_to_upload}

        try:
            result = requests.post('https://wpa-sec.stanev.org/?submit',
                    headers=headers,
                    files=payload,
                    timeout=timeout)
            if ' already submitted' in result.text:
                logging.warning(f"{path} was already submitted.")
        except requests.exceptions.RequestException as e:
            logging.error(f"WPA_SEC: Got an exception while uploading {path} -> {e}")
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
            logging.info("WPA_SEC: Internet connectivity detected.\
                          Uploading new handshakes to wpa-sec.stanev.org")

            for idx, handshake in enumerate(handshake_new):
                display.set('status', f"Uploading handshake to wpa-sec.stanev.org ({idx + 1}/{len(handshake_new)})")
                display.update(force=True)
                try:
                    _upload_to_wpasec(handshake)
                    ALREADY_UPLOADED.append(handshake)
                    with open('/root/.wpa_sec_uploads', 'a') as f:
                        f.write(handshake + "\n")
                    logging.info(f"WPA_SEC: Successfuly uploaded {handshake}")
                except requests.exceptions.RequestException:
                    pass
                except OSError as os_e:
                    logging.error(f"WPA_SEC: Got the following error: {os_e}")
