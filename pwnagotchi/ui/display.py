import _thread
from threading import Lock

import shutil
import logging
import pwnagotchi, pwnagotchi.plugins as plugins

import pwnagotchi.ui.hw as hw
from pwnagotchi.ui.view import View

from http.server import BaseHTTPRequestHandler, HTTPServer


class VideoHandler(BaseHTTPRequestHandler):
    _lock = Lock()
    _index = """<html>
  <head>
      <title>%s</title>
      <style>
        .block {
          -webkit-appearance: button;
          -moz-appearance: button;
          appearance: button;

          display: block;
          cursor: pointer;
          text-align: center;
        }
    </style>
  </head>
  <body>
    <div style="position: absolute; top:0; left:0; width:100%%;">
        <img src="/ui" id="ui" style="width:100%%"/>
        <br/>
        <hr/>
        <form action="/shutdown" onsubmit="return confirm('This will halt the unit, continue?');">
            <input type="submit" class="block" value="Shutdown"/>
        </form>
    </div>
    
    <script type="text/javascript">
    window.onload = function() {
        var image = document.getElementById("ui");
        function updateImage() {
            image.src = image.src.split("?")[0] + "?" + new Date().getTime();
        }
        setInterval(updateImage, %d);
    }
    </script>
  </body>
</html>"""

    @staticmethod
    def render(img):
        with VideoHandler._lock:
            img.save("/root/pwnagotchi.png", format='PNG')

    def log_message(self, format, *args):
        return

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            try:
                self.wfile.write(bytes(self._index % (pwnagotchi.name(), 1000), "utf8"))
            except:
                pass

        elif self.path.startswith('/shutdown'):
            pwnagotchi.shutdown()

        elif self.path.startswith('/ui'):
            with self._lock:
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                try:
                    with open("/root/pwnagotchi.png", 'rb') as fp:
                        shutil.copyfileobj(fp, self.wfile)
                except:
                    pass
        else:
            self.send_response(404)


class Display(View):
    def __init__(self, config, state={}):
        super(Display, self).__init__(config, hw.display_for(config), state)
        self._enabled = config['ui']['display']['enabled']
        self._rotation = config['ui']['display']['rotation']
        self._video_enabled = config['ui']['display']['video']['enabled']
        self._video_port = config['ui']['display']['video']['port']
        self._video_address = config['ui']['display']['video']['address']
        self._httpd = None

        self.init_display()

        if self._video_enabled:
            _thread.start_new_thread(self._http_serve, ())

    def _http_serve(self):
        if self._video_address is not None:
            self._httpd = HTTPServer((self._video_address, self._video_port), VideoHandler)
            logging.info("ui available at http://%s:%d/" % (self._video_address, self._video_port))
            self._httpd.serve_forever()
        else:
            logging.info("could not get ip of usb0, video server not starting")

    def is_inky(self):
        return self._implementation.name == 'inky'

    def is_papirus(self):
        return self._implementation.name == 'papirus'

    def is_waveshare_v1(self):
        return self._implementation.name == 'waveshare_1'

    def is_waveshare_v2(self):
        return self._implementation.name == 'waveshare_2'

    def is_oledhat(self):
        return self._implementation.name == 'oledhat'

    def is_waveshare_any(self):
        return self.is_waveshare_v1() or self.is_waveshare_v2()

    def init_display(self):
        if self._enabled:
            self._implementation.initialize()
            plugins.on('display_setup', self._implementation)
        else:
            logging.warning("display module is disabled")
        self.on_render(self._on_view_rendered)

    def clear(self):
        self._implementation.clear()

    def image(self):
        img = None
        if self._canvas is not None:
            img = self._canvas if self._rotation == 0 else self._canvas.rotate(-self._rotation)
        return img

    def _on_view_rendered(self, img):
        VideoHandler.render(img)
        if self._enabled:
            self._canvas = (img if self._rotation == 0 else img.rotate(self._rotation))
            if self._implementation is not None:
                self._implementation.render(self._canvas)
