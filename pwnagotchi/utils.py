from datetime import datetime
from enum import Enum
import logging
import glob
import os
import time
import subprocess
import yaml
import json


# https://stackoverflow.com/questions/823196/yaml-merge-in-python
def merge_config(user, default):
    if isinstance(user, dict) and isinstance(default, dict):
        for k, v in default.items():
            if k not in user:
                user[k] = v
            else:
                user[k] = merge_config(user[k], v)
    return user


def load_config(args):
    with open(args.config) as fp:
        config = yaml.safe_load(fp)

    if os.path.exists(args.user_config):
        with open(args.user_config) as fp:
            user_config = yaml.safe_load(fp)
            # if the file is empty, safe_load will return None and merge_config will boom.
            if user_config:
                config = merge_config(user_config, config)

    return config


def setup_logging(args, config):
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    root = logging.getLogger()

    root.setLevel(logging.DEBUG if args.debug else logging.INFO)

    if config['main']['log']:
        file_handler = logging.FileHandler(config['main']['log'])
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)


def secs_to_hhmmss(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)


def total_unique_handshakes(path):
    expr = os.path.join(path, "*.pcap")
    return len(glob.glob(expr))


def iface_channels(ifname):
    channels = []
    output = subprocess.getoutput("/sbin/iwlist %s freq" % ifname)
    for line in output.split("\n"):
        line = line.strip()
        if line.startswith("Channel "):
            channels.append(int(line.split()[1]))
    return channels


def led(on=True):
    with open('/sys/class/leds/led0/brightness', 'w+t') as fp:
        fp.write("%d" % (0 if on is True else 1))


def blink(times=1, delay=0.3):
    for t in range(0, times):
        led(True)
        time.sleep(delay)
        led(False)
        time.sleep(delay)
    led(True)

class WifiInfo(Enum):
    """
    Fields you can extract from a pcap file
    """
    BSSID = 0
    ESSID = 1
    ENCRYPTION = 2
    CHANNEL = 3
    RSSI = 4

class FieldNotFoundError(Exception):
    pass


def extract_from_pcap(path, fields):
    """
    Search in pcap-file for specified information

    path: Path to pcap file
    fields: Array of fields that should be extracted

    If a field is not found, FieldNotFoundError is raised
    """
    results = dict()
    for field in fields:
        if not isinstance(field, WifiInfo):
            raise TypeError("Invalid field")

        subtypes = set()

        if field == WifiInfo.BSSID:
            from scapy.all import Dot11Beacon, Dot11ProbeResp, Dot11AssoReq, Dot11ReassoReq, Dot11, sniff
            subtypes.add('beacon')
            bpf_filter = " or ".join([f"wlan type mgt subtype {subtype}" for subtype in subtypes])
            packets = sniff(offline=path, filter=bpf_filter)
            try:
                for packet in packets:
                    if packet.haslayer(Dot11Beacon):
                        if hasattr(packet[Dot11], 'addr3'):
                            results[field] = packet[Dot11].addr3
                            break
                else: # magic
                    raise FieldNotFoundError("Could not find field [BSSID]")
            except Exception:
                raise FieldNotFoundError("Could not find field [BSSID]")
        elif field == WifiInfo.ESSID:
            from scapy.all import Dot11Beacon, Dot11ReassoReq, Dot11AssoReq, Dot11, sniff, Dot11Elt
            subtypes.add('beacon')
            subtypes.add('assoc-req')
            subtypes.add('reassoc-req')
            bpf_filter = " or ".join([f"wlan type mgt subtype {subtype}" for subtype in subtypes])
            packets = sniff(offline=path, filter=bpf_filter)
            try:
                for packet in packets:
                    if packet.haslayer(Dot11Elt) and hasattr(packet[Dot11Elt], 'info'):
                        results[field] = packet[Dot11Elt].info.decode('utf-8')
                        break
                else: # magic
                    raise FieldNotFoundError("Could not find field [ESSID]")
            except Exception:
                raise FieldNotFoundError("Could not find field [ESSID]")
        elif field == WifiInfo.ENCRYPTION:
            from scapy.all import Dot11Beacon, sniff
            subtypes.add('beacon')
            bpf_filter = " or ".join([f"wlan type mgt subtype {subtype}" for subtype in subtypes])
            packets = sniff(offline=path, filter=bpf_filter)
            try:
                for packet in packets:
                    if packet.haslayer(Dot11Beacon) and hasattr(packet[Dot11Beacon], 'network_stats'):
                        stats = packet[Dot11Beacon].network_stats()
                        if 'crypto' in stats:
                            results[field] = stats['crypto'] # set with encryption types
                            break
                else: # magic
                    raise FieldNotFoundError("Could not find field [ENCRYPTION]")
            except Exception:
                raise FieldNotFoundError("Could not find field [ENCRYPTION]")
        elif field == WifiInfo.CHANNEL:
            from scapy.all import sniff, RadioTap
            from pwnagotchi.mesh.wifi import freq_to_channel
            packets = sniff(offline=path, count=1)
            try:
                results[field] = freq_to_channel(packets[0][RadioTap].ChannelFrequency)
            except Exception:
                raise FieldNotFoundError("Could not find field [CHANNEL]")
        elif field == WifiInfo.RSSI:
            from scapy.all import sniff, RadioTap
            from pwnagotchi.mesh.wifi import freq_to_channel
            packets = sniff(offline=path, count=1)
            try:
                results[field] = packets[0][RadioTap].dBm_AntSignal
            except Exception:
                raise FieldNotFoundError("Could not find field [RSSI]")

    return results


class StatusFile(object):
    def __init__(self, path, data_format='raw'):
        self._path = path
        self._updated = None
        self._format = data_format
        self.data = None

        if os.path.exists(path):
            self._updated = datetime.fromtimestamp(os.path.getmtime(path))
            with open(path) as fp:
                if data_format == 'json':
                    self.data = json.load(fp)
                else:
                    self.data = fp.read()

    def data_field_or(self, name, default=""):
        if self.data is not None and name in self.data:
            return self.data[name]
        return default

    def newer_then_minutes(self, minutes):
        return self._updated is not None and ((datetime.now() - self._updated).seconds / 60) < minutes

    def newer_then_days(self, days):
        return self._updated is not None and (datetime.now() - self._updated).days < days

    def update(self, data=None):
        self._updated = datetime.now()
        self.data = data
        with open(self._path, 'w') as fp:
            if data is None:
                fp.write(str(self._updated))

            elif self._format == 'json':
                json.dump(self.data, fp)

            else:
                fp.write(data)
