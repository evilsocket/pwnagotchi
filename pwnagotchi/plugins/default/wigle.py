__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '1.0.0'
__name__ = 'wigle'
__license__ = 'GPL3'
__description__ = 'This plugin automatically uploades collected wifis to wigle.net'

import os
import logging
import json
from io import StringIO
import csv
from datetime import datetime
import requests
from pwnagotchi.mesh.wifi import freq_to_channel
from pwnagotchi.utils import WifiInfo, FieldNotFoundError, extract_from_pcap

READY = False
ALREADY_UPLOADED = None
SKIP = None
OPTIONS = dict()

AKMSUITE_TYPES = {
    0x00: "Reserved",
    0x01: "802.1X",
    0x02: "PSK",
}

def _handle_packet(packet, result):
    from scapy.all import RadioTap, Dot11Elt, Dot11Beacon, rdpcap, Scapy_Exception, Dot11, Dot11ProbeResp, Dot11AssoReq, \
        Dot11ReassoReq, Dot11EltRSN, Dot11EltVendorSpecific, Dot11EltMicrosoftWPA
    """
    Analyze each packet and extract the data from Dot11 layers
    """

    if hasattr(packet, 'cap') and 'privacy' in packet.cap:
        # packet is encrypted
        if 'encryption' not in result:
            result['encryption'] = set()

    if packet.haslayer(Dot11Beacon):
        if packet.haslayer(Dot11Beacon)\
                or packet.haslayer(Dot11ProbeResp)\
                or packet.haslayer(Dot11AssoReq)\
                or packet.haslayer(Dot11ReassoReq):
            if 'bssid' not in result and hasattr(packet[Dot11], 'addr3'):
                result['bssid'] = packet[Dot11].addr3
            if 'essid' not in result and hasattr(packet[Dot11Elt], 'info'):
                result['essid'] = packet[Dot11Elt].info
            if 'channel' not in result and hasattr(packet[Dot11Elt:3], 'info'):
                result['channel'] = int(ord(packet[Dot11Elt:3].info))

    if packet.haslayer(RadioTap):
        if 'rssi' not in result and hasattr(packet[RadioTap], 'dBm_AntSignal'):
            result['rssi'] = packet[RadioTap].dBm_AntSignal
        if 'channel' not in result and hasattr(packet[RadioTap], 'ChannelFrequency'):
            result['channel'] = freq_to_channel(packet[RadioTap].ChannelFrequency)

    # see: https://fossies.org/linux/scapy/scapy/layers/dot11.py
    if packet.haslayer(Dot11EltRSN):
        if hasattr(packet[Dot11EltRSN], 'akm_suites'):
            auth = AKMSUITE_TYPES.get(packet[Dot11EltRSN].akm_suites[0].suite)
            result['encryption'].add(f"WPA2/{auth}")
        else:
            result['encryption'].add("WPA2")

    if packet.haslayer(Dot11EltVendorSpecific)\
    and (packet.haslayer(Dot11EltMicrosoftWPA)
         or packet.info.startswith(b'\x00P\xf2\x01\x01\x00')):

        if hasattr(packet, 'akm_suites'):
            auth = AKMSUITE_TYPES.get(packet.akm_suites[0].suite)
            result['encryption'].add(f"WPA2/{auth}")
        else:
            result['encryption'].add("WPA2")
    # end see

    return result


def _analyze_pcap(pcap):
    from scapy.all import RadioTap, Dot11Elt, Dot11Beacon, rdpcap, Scapy_Exception, Dot11, Dot11ProbeResp, Dot11AssoReq, \
        Dot11ReassoReq, Dot11EltRSN, Dot11EltVendorSpecific, Dot11EltMicrosoftWPA
    """
    Iterate over the packets and extract data
    """
    result = dict()

    try:
        packets = rdpcap(pcap)
        for packet in packets:
            result = _handle_packet(packet, result)
    except Scapy_Exception as sc_e:
        raise sc_e

    return result


def on_loaded():
    """
    Gets called when the plugin gets loaded
    """
    global READY
    global ALREADY_UPLOADED
    global SKIP

    SKIP = list()

    if 'api_key' not in OPTIONS or ('api_key' in OPTIONS and OPTIONS['api_key'] is None):
        logging.error("WIGLE: api_key isn't set. Can't upload to wigle.net")
        return

    try:
        with open('/root/.wigle_uploads', 'r') as f:
            ALREADY_UPLOADED = f.read().splitlines()
    except OSError:
        logging.warning('WIGLE: No upload-file found.')
        ALREADY_UPLOADED = []

    READY = True


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

def _transform_wigle_entry(gps_data, pcap_data):
    """
    Transform to wigle entry in file
    """
    dummy = StringIO()
    # write kismet header
    dummy.write("WigleWifi-1.4,appRelease=20190201,model=Kismet,release=2019.02.01.{},device=kismet,display=kismet,board=kismet,brand=kismet\n")
    dummy.write("MAC,SSID,AuthMode,FirstSeen,Channel,RSSI,CurrentLatitude,CurrentLongitude,AltitudeMeters,AccuracyMeters,Type")

    writer = csv.writer(dummy, delimiter=",", quoting=csv.QUOTE_NONE)
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
        0, # accuracy?
        'WIFI'])
    return dummy.getvalue()

def _send_to_wigle(lines, api_key, timeout=30):
    """
    Uploads the file to wigle-net
    """

    dummy = StringIO()

    for line in lines:
        dummy.write(f"{line}")

    dummy.seek(0)

    headers = {'Authorization': f"Basic {api_key}",
               'Accept': 'application/json'}
    data = {'donate': 'false'}
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


def on_internet_available(display, keypair, config, log):
    from scapy.all import RadioTap, Dot11Elt, Dot11Beacon, rdpcap, Scapy_Exception, Dot11, Dot11ProbeResp, Dot11AssoReq, \
        Dot11ReassoReq, Dot11EltRSN, Dot11EltVendorSpecific, Dot11EltMicrosoftWPA
    """
    Called in manual mode when there's internet connectivity
    """
    global ALREADY_UPLOADED
    global SKIP

    if READY:
        handshake_dir = config['bettercap']['handshakes']
        all_files = os.listdir(handshake_dir)
        all_gps_files = [os.path.join(handshake_dir, filename)
                     for filename in all_files
                     if filename.endswith('.gps.json')]
        new_gps_files = set(all_gps_files) - set(ALREADY_UPLOADED) - set(SKIP)

        if new_gps_files:
            logging.info("WIGLE: Internet connectivity detected. Uploading new handshakes to wigle.net")

            csv_entries = list()
            no_err_entries = list()

            for gps_file in new_gps_files:
                pcap_filename = gps_file.replace('.gps.json', '.pcap')

                if not os.path.exists(pcap_filename):
                    logging.error("WIGLE: Can't find pcap for %s", gps_file)
                    SKIP.append(gps_file)
                    continue

                try:
                    gps_data = _extract_gps_data(gps_file)
                except OSError as os_err:
                    logging.error("WIGLE: %s", os_err)
                    SKIP.append(gps_file)
                    continue
                except json.JSONDecodeError as json_err:
                    logging.error("WIGLE: %s", json_err)
                    SKIP.append(gps_file)
                    continue

                try:
                    pcap_data = extract_from_pcap(pcap_filename, [WifiInfo.BSSID,
                                                                  WifiInfo.ESSID,
                                                                  WifiInfo.ENCRYPTION,
                                                                  WifiInfo.CHANNEL,
                                                                  WifiInfo.RSSI])
                except FieldNotFoundError:
                    logging.error("WIGLE: Could not extract all informations. Skip %s", gps_file)
                    SKIP.append(gps_file)
                    continue
                except Scapy_Exception as sc_e:
                    logging.error("WIGLE: %s", sc_e)
                    SKIP.append(gps_file)
                    continue

                new_entry = _transform_wigle_entry(gps_data, pcap_data)
                csv_entries.append(new_entry)
                no_err_entries.append(gps_file)

            if csv_entries:
                display.set('status', "Uploading gps-data to wigle.net ...")
                display.update(force=True)
                try:
                    _send_to_wigle(csv_entries, OPTIONS['api_key'])
                    ALREADY_UPLOADED += no_err_entries
                    with open('/root/.wigle_uploads', 'a') as up_file:
                        for gps in no_err_entries:
                            up_file.write(gps + "\n")
                    logging.info("WIGLE: Successfuly uploaded %d files", len(no_err_entries))
                except requests.exceptions.RequestException as re_e:
                    SKIP += no_err_entries
                    logging.error("WIGLE: Got an exception while uploading %s", re_e)
                except OSError as os_e:
                    SKIP += no_err_entries
                    logging.error("WIGLE: Got the following error: %s", os_e)
