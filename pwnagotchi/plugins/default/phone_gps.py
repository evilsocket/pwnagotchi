__author__ = 'spees <speeskonijn@gmail.com>'
__version__ = '1.0.0'
__name__ = 'phone_gps'
__license__ = 'GPL3'
__description__ = 'Save GPS coordinates whenever an handshake is captured using your phone built-in GPS over bluetooth.'

import logging
import json
import os
import subprocess
import pwnagotchi.ui.state as ui

dev = "/dev/rfcomm1"
mac = 0
a = 0
running = False
OPTIONS = dict()


def on_loaded():
    logging.info("phone gps plugin loaded")


def on_ready(agent):
    global a
    a = agent


def start():
    global running

    logging.info("enabling bettercap's gps module for %s" % dev)
    a.run('set gps.device %s' % dev)
    a.run('gps on')
    running = True
    logging.info("GPS ENABLED")


def on_handshake(agent, filename, access_point, client_station):
    if running:
        info = agent.session()
        gps = info['gps']
        gps_filename = filename.replace('.pcap', '.gps.json')

        logging.info("saving GPS to %s (%s)" % (gps_filename, gps))
        with open(gps_filename, 'w+t') as fp:
            json.dump(gps, fp)


def on_ui_update(ui):
    global mac, running

    if mac is not 0 and not running:
        connect_rfcomm(mac)
        start()
    elif mac == 0:
        get_connected_mac()
    elif running:
        ui.set("bluetooth", "+GPS")


def on_internet_available(agent):
    if running:
        logging.info("Checking GPS connection...")
        check_connection()


def check_connection():
    con = subprocess.run(('rfcomm | awk \'{print $7}\''),
                            shell=True, universal_newlines=True, encoding='utf-8', capture_output=True)
    if con.stdout.strip() == 'closed' or con.stdout.strip() == '':
        logging.info("Reconnecting GPS..")
        connect_rfcomm(mac)


def find_rfcomm_port():
    port = subprocess.run(('/usr/bin/sdptool browse '+mac+' | grep Serial -C 3 | grep Channel | awk \'{print $2}\''), 
                            shell=True, universal_newlines=True, encoding='utf-8', capture_output=True)
    return port.stdout.strip()


def get_connected_mac():
    global mac
    mac = subprocess.run(('/usr/bin/hcitool con | awk \'{print $3}\''), 
                            shell=True, universal_newlines=True, encoding='utf-8', capture_output=True)
    mac = mac.stdout.strip()
    if mac == '':
        mac = 0


def connect_rfcomm(mac):
    ports = find_rfcomm_port()
    for p in ports.split("\n"):
        subprocess.Popen(('rfcomm connect '+dev+' '+mac+' '+p),
                            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
