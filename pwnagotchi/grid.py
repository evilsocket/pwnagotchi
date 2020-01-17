import subprocess
import socket
import requests
import json
import logging

import pwnagotchi

# pwngrid-peer is running on port 8666
API_ADDRESS = "http://127.0.0.1:8666/api/v1"


def is_connected():
    try:
        # check DNS
        host = socket.gethostbyname('api.pwnagotchi.ai')
        if host:
            # check connectivity itself
            socket.create_connection((host, 443), timeout=30)
            return True
    except:
        pass
    return False


def call(path, obj=None):
    url = '%s%s' % (API_ADDRESS, path)
    if obj is None:
        r = requests.get(url, headers=None, timeout=(30.0, 60.0))
    elif isinstance(obj, dict):
        r = requests.post(url, headers=None, json=obj, timeout=(30.0, 60.0))
    else:
        r = requests.post(url, headers=None, data=obj, timeout=(30.0, 60.0))

    if r.status_code != 200:
        raise Exception("(status %d) %s" % (r.status_code, r.text))
    return r.json()


def advertise(enabled=True):
    return call("/mesh/%s" % 'true' if enabled else 'false')


def set_advertisement_data(data):
    return call("/mesh/data", obj=data)


def get_advertisement_data():
    return call("/mesh/data")


def memory():
    return call("/mesh/memory")


def peers():
    return call("/mesh/peers")


def closest_peer():
    all = peers()
    return all[0] if len(all) else None


def update_data(last_session):
    brain = {}
    try:
        with open('/root/brain.json') as fp:
            brain = json.load(fp)
    except:
        pass

    data = {
        'session': {
            'duration': last_session.duration,
            'epochs': last_session.epochs,
            'train_epochs': last_session.train_epochs,
            'avg_reward': last_session.avg_reward,
            'min_reward': last_session.min_reward,
            'max_reward': last_session.max_reward,
            'deauthed': last_session.deauthed,
            'associated': last_session.associated,
            'handshakes': last_session.handshakes,
            'peers': last_session.peers,
        },
        'uname': subprocess.getoutput("uname -a"),
        'brain': brain,
        'version': pwnagotchi.__version__
    }

    logging.debug("updating grid data: %s" % data)

    call("/data", data)


def report_ap(essid, bssid):
    try:
        call("/report/ap", {
            'essid': essid,
            'bssid': bssid,
        })
        return True
    except Exception as e:
        logging.exception("error while reporting ap %s(%s)" % (essid, bssid))

    return False


def inbox(page=1, with_pager=False):
    obj = call("/inbox?p=%d" % page)
    return obj["messages"] if not with_pager else obj


def inbox_message(id):
    return call("/inbox/%d" % int(id))


def mark_message(id, mark):
    return call("/inbox/%d/%s" % (int(id), str(mark)))


def send_message(to, message):
    return call("/unit/%s/inbox" % to, message.encode('utf-8'))
