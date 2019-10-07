from datetime import datetime
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
    with open(args.config, 'rt') as fp:
        config = yaml.safe_load(fp)

    if os.path.exists(args.user_config):
        with open(args.user_config, 'rt') as fp:
            user_config = yaml.safe_load(fp)
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
