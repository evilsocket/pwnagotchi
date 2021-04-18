import os
import logging
import json
import csv
import requests

from io import StringIO
from datetime import datetime
from pwnagotchi.utils import WifiInfo, FieldNotFoundError, extract_from_pcap, StatusFile, remove_whitelisted
from threading import Lock
from pwnagotchi import plugins
from pwnagotchi._version import __version__ as __pwnagotchi_version__


def _extract_gps_data(path):
    """
    Extract data from gps-file

    return json-obj
    """

    try:
        with open(path, 'r') as json_file:
            return json.load(json_file)
    except OSError as os_err:
        raise os_err
    except json.JSONDecodeError as json_err:
        raise json_err


def _format_auth(data):
    out = ""
    for auth in data:
        out = f"{out}[{auth}]"
    return out


def _transform_wigle_entry(gps_data, pcap_data, plugin_version):
    """
    Transform to wigle entry in file
    """
    dummy = StringIO()
    # write kismet header
    dummy.write(
        "WigleWifi-1.4,appRelease={},model=pwnagotchi,release={},device=pwnagotchi,display=kismet,board=kismet,brand=pwnagotchi\n".format(plugin_version, __pwnagotchi_version__))
    dummy.write(
        "MAC,SSID,AuthMode,FirstSeen,Channel,RSSI,CurrentLatitude,CurrentLongitude,AltitudeMeters,AccuracyMeters,Type")

    writer = csv.writer(dummy, delimiter=",", quoting=csv.QUOTE_NONE, escapechar="\\")
    writer.writerow([
        pcap_data[WifiInfo.BSSID],
        pcap_data[WifiInfo.ESSID],
        _format_auth(pcap_data[WifiInfo.ENCRYPTION]),
        datetime.strptime(gps_data['Updated'].rsplit('.')[0],
                          "%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%d %H:%M:%S'),
        pcap_data[WifiInfo.CHANNEL],
        pcap_data[WifiInfo.RSSI],
        gps_data['Latitude'],
        gps_data['Longitude'],
        gps_data['Altitude'],
        0,  # accuracy?
        'WIFI'])
    return dummy.getvalue()


def _send_to_wigle(lines, api_key, donate=True, timeout=30):
    """
    Uploads the file to wigle-net
    """

    dummy = StringIO()

    for line in lines:
        dummy.write(f"{line}")

    dummy.seek(0)

    headers = {'Authorization': f"Basic {api_key}",
               'Accept': 'application/json'}
    data = {'donate': 'on' if donate else 'false'}
    payload = {'file': dummy, 'type': 'text/csv'}

    try:
        res = requests.post('https://api.wigle.net/api/v2/file/upload',
                            data=data,
                            headers=headers,
                            files=payload,
                            timeout=timeout)
        json_res = res.json()
        if not json_res['success']:
            raise requests.exceptions.RequestException(json_res['message'])
    except requests.exceptions.RequestException as re_e:
        raise re_e


class Wigle(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '2.0.0'
    __license__ = 'GPL3'
    __description__ = 'This plugin automatically uploads collected wifis to wigle.net'

    def __init__(self):
        self.ready = False
        self.report = StatusFile('/root/.wigle_uploads', data_format='json')
        self.skip = list()
        self.lock = Lock()

    def on_loaded(self):
        if 'api_key' not in self.options or ('api_key' in self.options and self.options['api_key'] is None):
            logging.debug("WIGLE: api_key isn't set. Can't upload to wigle.net")
            return

        if not 'whitelist' in self.options:
            self.options['whitelist'] = list()

        if not 'donate' in self.options:
            self.options['donate'] = True

        self.ready = True

    def on_internet_available(self, agent):
        """
        Called in manual mode when there's internet connectivity
        """
        if not self.ready or self.lock.locked():
            return

        from scapy.all import Scapy_Exception

        config = agent.config()
        display = agent.view()
        reported = self.report.data_field_or('reported', default=list())
        handshake_dir = config['bettercap']['handshakes']
        all_files = os.listdir(handshake_dir)
        all_gps_files = [os.path.join(handshake_dir, filename)
                         for filename in all_files
                         if filename.endswith('.gps.json')]

        all_gps_files = remove_whitelisted(all_gps_files, self.options['whitelist'])
        new_gps_files = set(all_gps_files) - set(reported) - set(self.skip)
        if new_gps_files:
            logging.info("WIGLE: Internet connectivity detected. Uploading new handshakes to wigle.net")
            csv_entries = list()
            no_err_entries = list()
            for gps_file in new_gps_files:
                pcap_filename = gps_file.replace('.gps.json', '.pcap')
                if not os.path.exists(pcap_filename):
                    logging.debug("WIGLE: Can't find pcap for %s", gps_file)
                    self.skip.append(gps_file)
                    continue
                try:
                    gps_data = _extract_gps_data(gps_file)
                except OSError as os_err:
                    logging.debug("WIGLE: %s", os_err)
                    self.skip.append(gps_file)
                    continue
                except json.JSONDecodeError as json_err:
                    logging.debug("WIGLE: %s", json_err)
                    self.skip.append(gps_file)
                    continue
                if gps_data['Latitude'] == 0 and gps_data['Longitude'] == 0:
                    logging.debug("WIGLE: Not enough gps-information for %s. Trying again next time.", gps_file)
                    self.skip.append(gps_file)
                    continue
                try:
                    pcap_data = extract_from_pcap(pcap_filename, [WifiInfo.BSSID,
                                                                  WifiInfo.ESSID,
                                                                  WifiInfo.ENCRYPTION,
                                                                  WifiInfo.CHANNEL,
                                                                  WifiInfo.RSSI])
                except FieldNotFoundError:
                    logging.debug("WIGLE: Could not extract all information. Skip %s", gps_file)
                    self.skip.append(gps_file)
                    continue
                except Scapy_Exception as sc_e:
                    logging.debug("WIGLE: %s", sc_e)
                    self.skip.append(gps_file)
                    continue
                new_entry = _transform_wigle_entry(gps_data, pcap_data, self.__version__)
                csv_entries.append(new_entry)
                no_err_entries.append(gps_file)
            if csv_entries:
                display.on_uploading('wigle.net')

                try:
                    _send_to_wigle(csv_entries, self.options['api_key'], donate=self.options['donate'])
                    reported += no_err_entries
                    self.report.update(data={'reported': reported})
                    logging.info("WIGLE: Successfully uploaded %d files", len(no_err_entries))
                except requests.exceptions.RequestException as re_e:
                    self.skip += no_err_entries
                    logging.debug("WIGLE: Got an exception while uploading %s", re_e)
                except OSError as os_e:
                    self.skip += no_err_entries
                    logging.debug("WIGLE: Got the following error: %s", os_e)

                display.on_normal()
