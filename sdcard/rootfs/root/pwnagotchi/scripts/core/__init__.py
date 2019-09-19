import sys
import glob
import os
import time
import subprocess
from threading import Lock
from datetime import datetime

logfile = None
loglock = Lock()


def log(msg):
    tstamp = str(datetime.now())
    line = "[%s] %s" % (tstamp, msg.rstrip())
    print(line)
    sys.stdout.flush()
    if logfile is not None:
        with loglock:
            with open(logfile, 'a+t') as fp:
                fp.write("%s\n" % line)


def secs_to_hhmmss(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)


def total_unique_handshakes(path):
    expr = os.path.join(path, "*.pcap")
    return len(glob.glob(expr))


def iface_address(ifname):
    output = subprocess.getoutput("/usr/sbin/ifconfig %s" % ifname)
    for line in output.split("\n"):
        line = line.strip()
        if line.startswith("inet "):
            return line.split(' ')[1].strip()
    return None

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
