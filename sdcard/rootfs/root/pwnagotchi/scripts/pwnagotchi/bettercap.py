import logging
import requests
from requests.auth import HTTPBasicAuth


class Client(object):
    def __init__(self, hostname='localhost', scheme='http', port=8081, username='user', password='pass'):
        self.hostname = hostname
        self.scheme = scheme
        self.port = port
        self.username = username
        self.password = password
        self.url = "%s://%s:%d/api" % (scheme, hostname, port)
        self.auth = HTTPBasicAuth(username, password)

    def _decode(self, r, verbose_errors=True):
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

    def session(self):
        r = requests.get("%s/session" % self.url, auth=self.auth)
        return self._decode(r)

    def events(self):
        r = requests.get("%s/events" % self.url, auth=self.auth)
        return self._decode(r)

    def run(self, command, verbose_errors=True):
        r = requests.post("%s/session" % self.url, auth=self.auth, json={'cmd': command})
        return self._decode(r, verbose_errors=verbose_errors)
