__author__ = 'evilsocket@gmail.com'
__version__ = '1.0.1'
__name__ = 'grid'
__license__ = 'GPL3'
__description__ = 'This plugin signals the unit cryptographic identity and list of pwned networks and list of pwned ' \
                  'networks to api.pwnagotchi.ai '

import os
import logging
import time
import glob

import pwnagotchi.grid as grid
import pwnagotchi.utils as utils
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.utils import WifiInfo, extract_from_pcap

OPTIONS = dict()
REPORT = utils.StatusFile('/root/.api-report.json', data_format='json')

UNREAD_MESSAGES = 0
TOTAL_MESSAGES = 0


def on_loaded():
    logging.info("grid plugin loaded.")


def parse_pcap(filename):
    logging.info("grid: parsing %s ..." % filename)

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
        logging.error("grid: %s" % e)

    return info[WifiInfo.ESSID], info[WifiInfo.BSSID]


def is_excluded(what):
    for skip in OPTIONS['exclude']:
        skip = skip.lower()
        what = what.lower()
        if skip in what or skip.replace(':', '') in what:
            return True
    return False


def on_ui_update(ui):
    if UNREAD_MESSAGES > 0:
        logging.debug("[grid] unread:%d total:%d" % (UNREAD_MESSAGES, TOTAL_MESSAGES))
        ui.on_unread_messages(UNREAD_MESSAGES, TOTAL_MESSAGES)


def set_reported(reported, net_id):
    global REPORT
    reported.append(net_id)
    REPORT.update(data={'reported': reported})


def on_internet_available(agent):
    global REPORT, UNREAD_MESSAGES, TOTAL_MESSAGES

    logging.debug("internet available")

    try:
        grid.update_data(agent.last_session)
    except Exception as e:
        logging.error("error connecting to the pwngrid-peer service: %s" % e)
        return

    try:
        logging.debug("checking mailbox ...")

        messages = grid.inbox()
        TOTAL_MESSAGES = len(messages)
        UNREAD_MESSAGES = len([m for m in messages if m['seen_at'] is None])

        if TOTAL_MESSAGES:
            on_ui_update(agent.view())
            logging.debug(" %d unread messages of %d total" % (UNREAD_MESSAGES, TOTAL_MESSAGES))

        logging.debug("checking pcaps")

        pcap_files = glob.glob(os.path.join(agent.config()['bettercap']['handshakes'], "*.pcap"))
        num_networks = len(pcap_files)
        reported = REPORT.data_field_or('reported', default=[])
        num_reported = len(reported)
        num_new = num_networks - num_reported

        if num_new > 0:
            if OPTIONS['report']:
                logging.info("grid: %d new networks to report" % num_new)
                logging.debug("OPTIONS: %s" % OPTIONS)
                logging.debug("  exclude: %s" % OPTIONS['exclude'])

                for pcap_file in pcap_files:
                    net_id = os.path.basename(pcap_file).replace('.pcap', '')
                    if net_id not in reported:
                        if is_excluded(net_id):
                            logging.debug("skipping %s due to exclusion filter" % pcap_file)
                            set_reported(reported, net_id)
                            continue

                        essid, bssid = parse_pcap(pcap_file)
                        if bssid:
                            if is_excluded(essid) or is_excluded(bssid):
                                logging.debug("not reporting %s due to exclusion filter" % pcap_file)
                                set_reported(reported, net_id)
                            else:
                                if grid.report_ap(essid, bssid):
                                    set_reported(reported, net_id)
                                time.sleep(1.5)
                        else:
                            logging.warning("no bssid found?!")
            else:
                logging.debug("grid: reporting disabled")

    except Exception as e:
        logging.error("grid api: %s" % e)
