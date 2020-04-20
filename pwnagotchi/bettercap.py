import json
import logging
import requests
import websockets

from requests.auth import HTTPBasicAuth


def decode(r, verbose_errors=True):
    try:
        return r.json()
    except Exception as e:
        if r.status_code == 200:
            logging.error("error while decoding json: error='%s' resp='%s'" % (e, r.text))
        else:
            err = "error %d: %s" % (r.status_code, r.text.strip())
            if verbose_errors:
                logging.info(err)
            raise Exception(err)
        return r.text


class Client(object):
    def __init__(self, hostname='localhost', scheme='http', port=8081, username='user', password='pass'):
        self.hostname = hostname
        self.scheme = scheme
        self.port = port
        self.username = username
        self.password = password
        self.url = "%s://%s:%d/api" % (scheme, hostname, port)
        self.websocket = "ws://%s:%s@%s:%d/api" % (username, password, hostname, port)
        self.auth = HTTPBasicAuth(username, password)

    def session(self):
        r = requests.get("%s/session" % self.url, auth=self.auth)
        return decode(r)

    async def start_websocket(self, consumer):
        s = "%s/events" % self.websocket
        while True:
            try:
                async with websockets.connect(s, ping_interval=60, ping_timeout=90) as ws:
                    async for msg in ws:
                        try:
                            await consumer(msg)
                        except Exception as ex:
                            logging.debug("Error while parsing event (%s)", ex)
            except websockets.exceptions.ConnectionClosedError:
                logging.debug("Lost websocket connection. Reconnecting...")
            except websockets.exceptions.WebSocketException as wex:
                logging.debug("Websocket exception (%s)", wex)

    def run(self, command, verbose_errors=True):
        r = requests.post("%s/session" % self.url, auth=self.auth, json={'cmd': command})
        return decode(r, verbose_errors=verbose_errors)
