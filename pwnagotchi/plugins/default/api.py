__author__ = 'evilsocket@gmail.com'
__version__ = '1.0.0'
__name__ = 'api'
__license__ = 'GPL3'
__description__ = 'This plugin signals the unit cryptographic identity to api.pwnagotchi.ai'

import logging
import json
import requests
import subprocess
import pwnagotchi
from pwnagotchi.utils import StatusFile

OPTIONS = dict()
READY = False
STATUS = StatusFile('/root/.api-enrollment.json')


def on_loaded():
    logging.info("api plugin loaded.")


def on_internet_available(ui, keypair, config, log):
    global STATUS

    if STATUS.newer_then_minutes(25):
        return

    try:
        logging.info("api: signign enrollment request ...")

        identity = "%s@%s" % (pwnagotchi.name(), keypair.fingerprint)
        # sign the identity string to prove we own both keys
        _, signature_b64 = keypair.sign(identity)

        api_address = 'https://api.pwnagotchi.ai/api/v1/unit/enroll'
        enroll = {
            'identity': identity,
            'public_key': keypair.pub_key_pem_b64,
            'signature': signature_b64,
            'data': {
                'duration': log.duration,
                'epochs': log.epochs,
                'train_epochs': log.train_epochs,
                'avg_reward': log.avg_reward,
                'min_reward': log.min_reward,
                'max_reward': log.max_reward,
                'deauthed': log.deauthed,
                'associated': log.associated,
                'handshakes': log.handshakes,
                'peers': log.peers,
                'uname': subprocess.getoutput("uname -a")
            }
        }

        logging.info("api: enrolling unit to %s ..." % api_address)
        r = requests.post(api_address, json=enroll)
        if r.status_code == 200:
            token = r.json()
            logging.info("api: enrolled")
            STATUS.update(data=json.dumps(token))
        else:
            logging.error("error %d: %s" % (r.status_code, r.json()))

    except Exception as e:
        logging.exception("error while enrolling the unit")
