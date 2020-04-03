import os
import logging
import time
import glob
import re

import pwnagotchi.grid as grid
import pwnagotchi.plugins as plugins
from pwnagotchi.utils import StatusFile, WifiInfo, extract_from_pcap
from threading import Lock


def parse_pcap(filename):
    logging.info("grid: parsing %s ..." % filename)

    net_id = os.path.basename(filename).replace('.pcap', '')

    if '_' in net_id:
        # /root/handshakes/ESSID_BSSID.pcap
        essid, bssid = net_id.split('_')
    else:
        # /root/handshakes/BSSID.pcap
        essid, bssid = '', net_id

    mac_re = re.compile('[0-9a-fA-F]{12}')
    if not mac_re.match(bssid):
        return '', ''

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


class Grid(plugins.Plugin):
    __author__ = 'evilsocket@gmail.com'
    __version__ = '1.0.1'
    __license__ = 'GPL3'
    __description__ = 'This plugin signals the unit cryptographic identity and list of pwned networks and list of pwned ' \
                      'networks to api.pwnagotchi.ai '

    def __init__(self):
        self.options = dict()
        self.report = StatusFile('/root/.api-report.json', data_format='json')

        self.unread_messages = 0
        self.total_messages = 0
        self.lock = Lock()

    def is_excluded(self, what):
        for skip in self.options['exclude']:
            skip = skip.lower()
            what = what.lower()
            if skip in what or skip.replace(':', '') in what:
                return True
        return False

    def on_loaded(self):
        logging.info("grid plugin loaded.")

    def set_reported(self, reported, net_id):
        if net_id not in reported:
            reported.append(net_id)
        self.report.update(data={'reported': reported})

    def check_inbox(self, agent):
        logging.debug("checking mailbox ...")
        messages = grid.inbox()
        self.total_messages = len(messages)
        self.unread_messages = len([m for m in messages if m['seen_at'] is None])

        if self.unread_messages:
            plugins.on('unread_inbox', self.unread_messages)
            logging.debug("[grid] unread:%d total:%d" % (self.unread_messages, self.total_messages))
            agent.view().on_unread_messages(self.unread_messages, self.total_messages)

    def check_handshakes(self, agent):
        logging.debug("checking pcaps")

        pcap_files = glob.glob(os.path.join(agent.config()['bettercap']['handshakes'], "*.pcap"))
        num_networks = len(pcap_files)
        reported = self.report.data_field_or('reported', default=[])
        num_reported = len(reported)
        num_new = num_networks - num_reported

        if num_new > 0:
            if self.options['report']:
                logging.info("grid: %d new networks to report" % num_new)
                logging.debug("self.options: %s" % self.options)
                logging.debug("  exclude: %s" % self.options['exclude'])

                for pcap_file in pcap_files:
                    net_id = os.path.basename(pcap_file).replace('.pcap', '')
                    if net_id not in reported:
                        if self.is_excluded(net_id):
                            logging.debug("skipping %s due to exclusion filter" % pcap_file)
                            self.set_reported(reported, net_id)
                            continue

                        essid, bssid = parse_pcap(pcap_file)
                        if bssid:
                            if self.is_excluded(essid) or self.is_excluded(bssid):
                                logging.debug("not reporting %s due to exclusion filter" % pcap_file)
                                self.set_reported(reported, net_id)
                            else:
                                if grid.report_ap(essid, bssid):
                                    self.set_reported(reported, net_id)
                                time.sleep(1.5)
                        else:
                            logging.warning("no bssid found?!")
            else:
                logging.debug("grid: reporting disabled")

    def on_internet_available(self, agent):
        logging.debug("internet available")

        if self.lock.locked():
            return

        with self.lock:
            try:
                grid.update_data(agent.last_session)
            except Exception as e:
                logging.error("error connecting to the pwngrid-peer service: %s" % e)
                logging.debug(e, exc_info=True)
                return

            try:
                self.check_inbox(agent)
            except Exception as e:
                logging.error("[grid] error while checking inbox: %s" % e)
                logging.debug(e, exc_info=True)

            try:
                self.check_handshakes(agent)
            except Exception as e:
                logging.error("[grid] error while checking pcaps: %s" % e)
                logging.debug(e, exc_info=True)
