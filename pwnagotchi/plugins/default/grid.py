__author__ = 'evilsocket@gmail.com'
__version__ = '1.0.0'
__name__ = 'grid'
__license__ = 'GPL3'
__description__ = 'This plugin signals the unit cryptographic identity and list of pwned networks and list of pwned networks to api.pwnagotchi.ai'

import os
import logging
import requests
import glob
import subprocess
import pwnagotchi
import pwnagotchi.utils as utils
from pwnagotchi.utils import WifiInfo, extract_from_pcap

OPTIONS = dict()
AUTH = utils.StatusFile('/root/.api-enrollment.json', data_format='json')
REPORT = utils.StatusFile('/root/.api-report.json', data_format='json')


def on_loaded():
    logging.info("api plugin loaded.")


def get_api_token(log, keys):
    global AUTH

    if AUTH.newer_then_minutes(25) and AUTH.data is not None and 'token' in AUTH.data:
        return AUTH.data['token']

    if AUTH.data is None:
        logging.info("api: enrolling unit ...")
    else:
        logging.info("api: refreshing token ...")

    identity = "%s@%s" % (pwnagotchi.name(), keys.fingerprint)
    # sign the identity string to prove we own both keys
    _, signature_b64 = keys.sign(identity)

    api_address = 'https://api.pwnagotchi.ai/api/v1/unit/enroll'
    enrollment = {
        'identity': identity,
        'public_key': keys.pub_key_pem_b64,
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

    r = requests.post(api_address, json=enrollment)
    if r.status_code != 200:
        raise Exception("(status %d) %s" % (r.status_code, r.json()))

    AUTH.update(data=r.json())

    logging.info("api: done")

    return AUTH.data["token"]


def parse_pcap(filename):
    logging.info("api: parsing %s ..." % filename)

    net_id = os.path.basename(filename).replace('.pcap', '')

    if '_' in net_id:
        # /root/handshakes/ESSID_BSSID.pcap
        essid, bssid = net_id.split('_')
    else:
        # /root/handshakes/BSSID.pcap
        essid, bssid = '', net_id

    it = iter(bssid)
    bssid = ':'.join([a + b for a, b in zip(it, it)])

    info = {
        WifiInfo.ESSID: essid,
        WifiInfo.BSSID: bssid,
    }

    try:
        info = extract_from_pcap(filename, [WifiInfo.BSSID, WifiInfo.ESSID])
    except Exception as e:
        logging.error("api: %s" % e)

    return info[WifiInfo.ESSID], info[WifiInfo.BSSID]


def api_report_ap(log, keys, token, essid, bssid):
    while True:
        token = AUTH.data['token']
        logging.info("api: reporting %s (%s)" % (essid, bssid))
        try:
            api_address = 'https://api.pwnagotchi.ai/api/v1/unit/report/ap'
            headers = {'Authorization': 'access_token %s' % token}
            report = {
                'essid': essid,
                'bssid': bssid,
            }
            r = requests.post(api_address, headers=headers, json=report)
            if r.status_code != 200:
                if r.status_code == 401:
                    logging.warning("token expired")
                    token = get_api_token(log, keys)
                    continue
                else:
                    raise Exception("(status %d) %s" % (r.status_code, r.text))
            else:
                return True
        except Exception as e:
            logging.error("api: %s" % e)
            return False


def on_internet_available(ui, keys, config, log):
    global REPORT

    try:

        pcap_files = glob.glob(os.path.join(config['bettercap']['handshakes'], "*.pcap"))
        num_networks = len(pcap_files)
        reported = REPORT.data_field_or('reported', default=[])
        num_reported = len(reported)
        num_new = num_networks - num_reported

        if num_new > 0:
            logging.info("api: %d new networks to report" % num_new)
            token = get_api_token(log, keys)

            if OPTIONS['report']:
                for pcap_file in pcap_files:
                    net_id = os.path.basename(pcap_file).replace('.pcap', '')
                    do_skip = False
                    for skip in OPTIONS['exclude']:
                        skip = skip.lower()
                        net = net_id.lower()
                        if skip in net or skip.replace(':', '') in net:
                            do_skip = True
                            break

                    if net_id not in reported and not do_skip:
                        essid, bssid = parse_pcap(pcap_file)
                        if bssid:
                            if api_report_ap(log, keys, token, essid, bssid):
                                reported.append(net_id)
                                REPORT.update(data={'reported': reported})
            else:
                logging.info("api: reporting disabled")

    except Exception as e:
        logging.exception("error while enrolling the unit")
