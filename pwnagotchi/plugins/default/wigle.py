import os
import logging
import json
from io import StringIO
import csv
from datetime import datetime
import requests
from pwnagotchi.utils import WifiInfo, FieldNotFoundError, extract_from_pcap, StatusFile
import pwnagotchi.plugins as plugins

'''
Since documentation is scant, I guess this is a place to say:
    Copy and paste the "Encoded for use" WiGLE API token into your pwnagotchi config.yaml
'''

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

def _create_kismet_wigle_csv(data_tuples):
    """
    Transform to wigle entry in file
    """

    # Reference: https://github.com/kismetwireless/kismet/blob/master/log_tools/kismetdb_to_wiglecsv.cc
    dummy = StringIO()
    # write kismet wigle csv header
    dummy.write('WigleWifi-1.4,appRelease=20190201,model=Kismet,release=2019.02.01.{},device=kismet,display=kismet,board=kismet,brand=kismet\r\n')
    dummy.write('MAC,SSID,AuthMode,FirstSeen,Channel,RSSI,CurrentLatitude,CurrentLongitude,AltitudeMeters,AccuracyMeters,Type\r\n')
    writer = csv.writer(dummy, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
    for data_tuple in data_tuples:
        gps_data = data_tuple[0]
        pcap_data = data_tuple[1]

        writer.writerow([
            pcap_data[WifiInfo.BSSID],
            pcap_data[WifiInfo.ESSID],
            ''.join(['[{}]'.format(y) for y in pcap_data[WifiInfo.ENCRYPTION]]),
            datetime.strptime(gps_data['Updated'].rsplit('.')[0],'%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'),
            pcap_data[WifiInfo.CHANNEL],
            pcap_data[WifiInfo.RSSI],
            gps_data['Latitude'],
            gps_data['Longitude'],
            gps_data['Altitude'],
            # Accuracy, in meters. According to gps.gov, the expected user range error should be below 7.8m, 95% of the time.
            # A global study, summarized by gps.gov on 2016-05-11, claims actual global URE was <= 0.715m, 95% of the time.
            # They also claim that a smartphone is typically accurate to within a 4.9m radius (2014-2015), though I'm not going to 
            # read the ~360 pages to find out if that includes positioning data based on the GSM network or just GNSS data:
            #   https://ion.org/publications/abstract.cfm?articleID=13079
            # So I'm just gonna yolo select 5m for accuracy, until I figure out why you put a 0 here or find a way to add accuracy.
            5,   
            'WIFI'])

    return dummy.getvalue()

def _send_to_wigle(csv_data, api_key, timeout=30):
    """
    Uploads the file to wigle-net
    """
    dummy = StringIO()
    dummy.write(csv_data)
    dummy.seek(0)

    headers = {'Authorization': 'Basic {}'.format(api_key), 'Accept': 'application/json'}
    data = {'donate': 'false'}
    payload = {'file': dummy, 'type': 'text/csv'}

    try:
        json_res = requests.post('https://api.wigle.net/api/v2/file/upload', data=data, headers=headers, files=payload, timeout=timeout).json()
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

    def on_loaded(self):
        if 'api_key' not in self.options or ('api_key' in self.options and self.options['api_key'] is None):
            logging.error("WIGLE: api_key isn't set. Can't upload to wigle.net")
            return
        self.ready = True

    def on_internet_available(self, agent):
        from scapy.all import Scapy_Exception
        """
        Called in manual mode when there's internet connectivity
        """

        # Anti-spaghet
        if not self.ready:
            return

        config = agent.config()
        display = agent.view()
        reported = self.report.data_field_or('reported', default=list())
        all_gps_files = [os.path.join(config['bettercap']['handshakes'], filename) for filename in os.listdir(config['bettercap']['handshakes']) if filename.endswith('.gps.json')]
        new_gps_files = set(all_gps_files) - set(reported) - set(self.skip)

        # Anti-spaghet
        if not new_gps_files:
            return
            
        logging.info("WIGLE: Internet connectivity detected. Uploading new handshakes to wigle.net")
        no_err_entries = list()
        data_tuples = []
        for gps_file in new_gps_files:
            pcap_filename = gps_file.replace('.gps.json', '.pcap')

            if not os.path.exists(pcap_filename):
                logging.error("WIGLE: Can't find pcap for %s", gps_file)
                self.skip.append(gps_file)
                continue

            try:
                gps_data = _extract_gps_data(gps_file)
            except OSError as os_err:
                logging.error("WIGLE: %s", os_err)
                self.skip.append(gps_file)
                continue
            except json.JSONDecodeError as json_err:
                logging.error("WIGLE: %s", json_err)
                self.skip.append(gps_file)
                continue

            if gps_data['Latitude'] == 0 and gps_data['Longitude'] == 0:
                logging.warning("WIGLE: Not enough gps-information for %s. Trying again next time.", gps_file)
                self.skip.append(gps_file)
                continue

            try:
                pcap_data = extract_from_pcap(pcap_filename, [WifiInfo.BSSID, WifiInfo.ESSID, WifiInfo.ENCRYPTION, WifiInfo.CHANNEL, WifiInfo.RSSI])
            except FieldNotFoundError:
                logging.error("WIGLE: Could not extract all information. Skip %s", gps_file)
                self.skip.append(gps_file)
                continue
            except Scapy_Exception as sc_e:
                logging.error("WIGLE: %s", sc_e)
                self.skip.append(gps_file)
                continue

            data_tuples.append((gps_data, pcap_data))
            no_err_entries.append(gps_file)

        # Anti-spaghet
        if len(data_tuples) == 0:
            return

        display.set('status', "Uploading gps-data to wigle.net ...")
        display.update(force=True)
        try:
            _send_to_wigle(_create_kismet_wigle_csv(data_tuples), self.options['api_key'])
            reported += no_err_entries
            self.report.update(data={'reported': reported})
            logging.info("WIGLE: Successfully uploaded one file with %s access points.", len(no_err_entries))
            
        # The previous exceptions here were as pointless as the one that follows:
        except Exception as e:
            # Ignoring valid Wigle data because we hit an exception doesn't seem like a good idea.
            # We would be throwing away legit, hard-earned data for things like "requests failed because internet sucks"
            logging.error("WIGLE: Encountered an exception while uploading Kismet Wigle CSV file: %s", str(e))
