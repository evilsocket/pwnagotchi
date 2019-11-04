import re
import _thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Lock
import shutil
import logging

import pwnagotchi
from pwnagotchi.agent import Agent
from pwnagotchi import plugins

frame_path = '/root/pwnagotchi.png'
frame_format = 'PNG'
frame_ctype = 'image/png'
frame_lock = Lock()


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
.pixelated {
  image-rendering:optimizeSpeed;             /* Legal fallback */
  image-rendering:-moz-crisp-edges;          /* Firefox        */
  image-rendering:-o-crisp-edges;            /* Opera          */
  image-rendering:-webkit-optimize-contrast; /* Safari         */
  image-rendering:optimize-contrast;         /* CSS3 Proposed  */
  image-rendering:crisp-edges;               /* CSS4 Proposed  */
  image-rendering:pixelated;                 /* CSS4 Proposed  */
  -ms-interpolation-mode:nearest-neighbor;   /* IE8+           */
}
"""

SCRIPT = """
window.onload = function() {
    var image = document.getElementById("ui");
    function updateImage() {
        image.src = image.src.split("?")[0] + "?" + new Date().getTime();
    }
    setInterval(updateImage, %d);
}
"""

INDEX = """<html>
  <head>
      <title>%s</title>
      <style>""" + STYLE + """</style>
  </head>
  <body>
    <div style="position: absolute; top:0; left:0; width:100%%;" class="pixelated">
        <img src="/ui" id="ui" style="width:100%%;"/>
        <br/>
        <hr/>
        <form style="display:inline;" method="POST" action="/shutdown" onsubmit="return confirm('This will halt the unit, continue?');">
            <input style="display:inline;" type="submit" class="block" value="Shutdown"/>
        </form>
        <form style="display:inline;" method="POST" action="/restart" onsubmit="return confirm('This will restart the service in %s mode, continue?');">
            <input style="display:inline;" type="submit" class="block" value="Restart in %s mode"/>
        </form>
    </div>

    <script type="text/javascript">""" + SCRIPT + """</script>
  </body>
</html>"""

STATUS_PAGE = """<html>
  <head>
      <title>%s</title>
      <style>""" + STYLE + """</style>
  </head>
  <body>
    <div style="position: absolute; top:0; left:0; width:100%%;">
        %s
    </div>
  </body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    AllowedOrigin = None  # CORS headers are not sent

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

    # just render some html in a 200 response
    def _html(self, html):
        self.send_response(200)
        self._send_cors_headers()
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        try:
            self.wfile.write(bytes(html, "utf8"))
        except:
            pass

    # serve the main html page
    def _index(self):
        other_mode = 'AUTO' if Agent.INSTANCE.mode == 'manual' else 'MANU'
        self._html(INDEX % (
            pwnagotchi.name(),
            1000, other_mode,
            other_mode))

    # serve a message and shuts down the unit
    def _shutdown(self):
        self._html(STATUS_PAGE % (pwnagotchi.name(), 'Shutting down ...'))
        pwnagotchi.shutdown()

    # serve a message and restart the unit in the other mode
    def _reboot(self):
        other_mode = 'AUTO' if Agent.INSTANCE.mode == 'manual' else 'MANU'
        self._html(STATUS_PAGE % (pwnagotchi.name(), 'Restart in %s mode ...' % other_mode))
        pwnagotchi.restart(other_mode)

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

        # TODO: FIX doesn't work with GET requests same-origin
        origin = self.headers.get('origin')
        if not origin:
            logging.warning("request with no Origin header from %s" % self.address_string())
            return False

        if origin != Handler.AllowedOrigin:
            logging.warning("request with blocked Origin from %s: %s" % (self.address_string(), origin))
            return False

        return True

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        if not self._is_allowed():
            return
        elif self.path.startswith('/shutdown'):
            self._shutdown()
        elif self.path.startswith('/restart'):
            self._restart()
        else:
            self.send_response(404)

    def do_GET(self):
        if not self._is_allowed():
            return
        elif self.path == '/':
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
            logging.info("web ui available at http://%s:%d/" % (self._address, self._port))
            self._httpd.serve_forever()
        else:
            logging.info("could not get ip of usb0, video server not starting")
