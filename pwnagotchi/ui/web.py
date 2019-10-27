import re
import _thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Lock
import shutil
import logging
import secrets
import http.cookies
from urllib.parse import parse_qs
import json

import pwnagotchi
from pwnagotchi import plugins

frame_path = '/root/pwnagotchi.png'
frame_format = 'PNG'
frame_ctype = 'image/png'
frame_lock = Lock()


CSRF_TOKEN_COOKIE_NAME = 'CSRF-TOKEN'
CSRF_TOKEN_HEADER_NAME = 'X-CSRF-TOKEN'
CSRF_TOKEN_DATA_NAME = 'CSRF-TOKEN'


def gen_csrf_token():
    return secrets.token_urlsafe()


def update_frame(img):
    global frame_lock, frame_path, frame_format
    with frame_lock:
        img.save(frame_path, format=frame_format)


STYLE = """
.block {
    -webkit-appearance: button;
    -moz-appearance: button;
    appearance: button;

    display: block;
    cursor: pointer;
    text-align: center;
}
"""

SCRIPT = """
window.onload = function() {
    var image = document.getElementById("ui");
    function updateImage() {
        image.src = image.src.split("?")[0] + "?" + new Date().getTime();
    }
    setInterval(updateImage, %(image_update_interval)d);
}
"""

INDEX = """<html>
  <head>
      <title>%(title)s</title>
      <style>""" + STYLE + """</style>
  </head>
  <body>
    <div style="position: absolute; top:0; left:0; width:100%%;">
        <img src="/ui" id="ui" style="width:100%%"/>
        <br/>
        <hr/>
        <form method="POST" action="/shutdown" onsubmit="return confirm('This will halt the unit, continue?');">
            %(csrf_input)s
            <input type="submit" class="block" value="Shutdown"/>
        </form>
    </div>

    <script type="text/javascript">""" + SCRIPT + """</script>
  </body>
</html>"""

SHUTDOWN = """<html>
  <head>
      <title>%(title)s</title>
      <style>""" + STYLE + """</style>
  </head>
  <body>
    <div style="position: absolute; top:0; left:0; width:100%%;">
        Shutting down ...
    </div>
  </body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    AllowedOrigin = None  # CORS headers are not sent

    def __init__(self, request, client_address, server):
        # if cookie is not set yet, but we need to add csrf token to html
        self._next_csrf_token = None

        super().__init__(request, client_address, server)

    # suppress internal logging
    def log_message(self, format, *args):
        return

    def _send_cors_headers(self):
        # misc security
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header("Referrer-Policy", "same-origin")
        # cors
        if Handler.AllowedOrigin:
            self.send_header("Access-Control-Allow-Origin", Handler.AllowedOrigin)
            self.send_header('Access-Control-Allow-Credentials', 'true')
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers",
                            "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")
            self.send_header("Vary", "Origin")

    def _get_csrf_cookie(self, gen_if_not_set=True):
        parsed_cookies = http.cookies.SimpleCookie()
        parsed_cookies.load(self.headers.get('Cookie', ''))

        csrf_token_cookie = parsed_cookies.get(CSRF_TOKEN_COOKIE_NAME)

        if csrf_token_cookie:
            return csrf_token_cookie.value

        if gen_if_not_set:
            self._next_csrf_token = self._next_csrf_token or gen_csrf_token()
            return self._next_csrf_token

    def _get_csrf_token_header(self):
        return self.headers.get(CSRF_TOKEN_HEADER_NAME)

    def _set_csrf_token(self):
        csrf_token_cookie = self._get_csrf_cookie(gen_if_not_set=False)

        if csrf_token_cookie:
            return

        self._next_csrf_token = self._next_csrf_token or gen_csrf_token()

        self.send_header(
            "Set-Cookie",
            f"{CSRF_TOKEN_COOKIE_NAME}={self._next_csrf_token}; Max-Age={60 * 60 * 24 * 365}; SameSite=Lax"
        )

    def _get_csrf_token_html_data(self):
        csrf_token = self._get_csrf_cookie()

        return {
            'csrf_input': f'<input type="hidden" name="{CSRF_TOKEN_DATA_NAME}" value="{csrf_token}"/>',
            'csrf_token_name': CSRF_TOKEN_DATA_NAME,
            'csrf_token': csrf_token
        }

    def _check_csrf_token(self, csrf_token=None):
        csrf_token_cookie = self._get_csrf_cookie(gen_if_not_set=False)
        csrf_token = csrf_token or self._get_csrf_token_header()

        if not csrf_token_cookie or not csrf_token:
            return False

        return secrets.compare_digest(csrf_token_cookie, csrf_token)

    # just render some html in a 200 response
    def _html(self, html):
        self.send_response(200)
        self._send_cors_headers()
        self._set_csrf_token()
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        try:
            self.wfile.write(bytes(html, "utf8"))
        except:
            pass

    # serve the main html page
    def _index(self):
        self._html(INDEX % {
            'title': pwnagotchi.name(),
            'image_update_interval': 1000,
            **self._get_csrf_token_html_data()
        })

    # serve a message and shuts down the unit
    def _shutdown(self):
        self._html(SHUTDOWN % {
            'title': pwnagotchi.name()
        })
        pwnagotchi.shutdown()

    # serve the PNG file with the display image
    def _image(self):
        global frame_lock, frame_path, frame_ctype

        with frame_lock:
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-type', frame_ctype)
            self.end_headers()
            try:
                with open(frame_path, 'rb') as fp:
                    shutil.copyfileobj(fp, self.wfile)
            except:
                pass

    # check the Origin header vs CORS
    def _is_allowed(self):
        if not Handler.AllowedOrigin or Handler.AllowedOrigin == '*':
            return True

        # TODO: FIX should check Referer header if Origin is not present
        origin = self.headers.get('origin')
        if not origin:
            logging.warning(f"request with no Origin header from {self.address_string()}")
            return False

        if origin != Handler.AllowedOrigin:
            logging.warning(f"request with blocked Origin from {self.address_string()}: {origin}")
            return False

        return True

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        if not self._is_allowed():
            self.send_error(403, 'Invalid Origin')
            return

        content_type = self.headers.get('Content-Type')
        content_len = int(self.headers.get('Content-Length'))
        body = self.rfile.read(content_len)

        if content_type == 'application/x-www-form-urlencoded':
            parsed_data = {
                # ignore repeated params, use only the latest
                key.decode('UTF-8'): values[-1].decode('UTF-8')
                for key, values in parse_qs(body, keep_blank_values=True).items()
            }
        elif content_type == 'application/json':
            parsed_data = json.loads(body)
        else:
            parsed_data = None

        csrf_token = (
            parsed_data.get(CSRF_TOKEN_DATA_NAME) if isinstance(parsed_data, dict) else None
        )
        if not self._check_csrf_token(csrf_token):
            self.send_error(403, 'Invalid CSRF token')
            return

        if self.path.startswith('/shutdown'):
            self._shutdown()
        else:
            self.send_response(404)

    def do_GET(self):
        if not self._is_allowed():
            self.send_error(403, 'Invalid Origin')
            return

        if self.path == '/':
            self._index()

        elif self.path.startswith('/ui'):
            self._image()

        elif self.path.startswith('/plugins'):
            matches = re.match(r'\/plugins\/([^\/]+)(\/.*)?', self.path)
            if matches:
                groups = matches.groups()
                plugin_name = groups[0]
                right_path = groups[1] if len(groups) == 2 else None
                plugins.one(plugin_name, 'webhook', self, right_path)

        else:
            self.send_response(404)


class Server(object):
    def __init__(self, config):
        self._enabled = config['video']['enabled']
        self._port = config['video']['port']
        self._address = config['video']['address']
        self._httpd = None

        if 'origin' in config['video']:
            Handler.AllowedOrigin = config['video']['origin']

        if self._enabled:
            _thread.start_new_thread(self._http_serve, ())

    def _http_serve(self):
        if self._address is not None:
            self._httpd = HTTPServer((self._address, self._port), Handler)
            logging.info(f"web ui available at http://{self._address}:{self._port}/")
            self._httpd.serve_forever()
        else:
            logging.info("could not get ip of usb0, video server not starting")
