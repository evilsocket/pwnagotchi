import _thread
from threading import Lock

import shutil
import logging
import os
import pwnagotchi, pwnagotchi.plugins as plugins

from pwnagotchi.ui.view import WHITE, View

from http.server import BaseHTTPRequestHandler, HTTPServer


class VideoHandler(BaseHTTPRequestHandler):
    _lock = Lock()
    _index = """<html>
  <head>
    <title>%s</title>
  </head>
  <body>
    <img src="/ui" id="ui"/>

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
        super(Display, self).__init__(config, state)
        self._enabled = config['ui']['display']['enabled']
        self._rotation = config['ui']['display']['rotation']
        self._video_enabled = config['ui']['display']['video']['enabled']
        self._video_port = config['ui']['display']['video']['port']
        self._video_address = config['ui']['display']['video']['address']
        self._display_type = config['ui']['display']['type']
        self._display_color = config['ui']['display']['color']

        self._render_cb = None
        self._display = None
        self._httpd = None

        if self._enabled:
            self._init_display()
        else:
            self.on_render(self._on_view_rendered)
            logging.warning("display module is disabled")

        if self._video_enabled:
            _thread.start_new_thread(self._http_serve, ())

    def _http_serve(self):
        if self._video_address is not None:
            self._httpd = HTTPServer((self._video_address, self._video_port), VideoHandler)
            logging.info("ui available at http://%s:%d/" % (self._video_address, self._video_port))
            self._httpd.serve_forever()
        else:
            logging.info("could not get ip of usb0, video server not starting")

    def _is_inky(self):
        return self._display_type in ('inkyphat', 'inky')

    def _is_papirus(self):
        return self._display_type in ('papirus', 'papi')

    def _is_waveshare_v1(self):
        return self._display_type in ('waveshare_1', 'ws_1', 'waveshare1', 'ws1')

    def _is_waveshare_v2(self):
        return self._display_type in ('waveshare_2', 'ws_2', 'waveshare2', 'ws2')

    def _is_waveshare(self):
        return self._is_waveshare_v1() or self._is_waveshare_v2()

    def _init_display(self):
        if self._is_inky():
            logging.info("initializing inky display")
            from inky import InkyPHAT
            self._display = InkyPHAT(self._display_color)
            self._display.set_border(InkyPHAT.BLACK)
            self._render_cb = self._inky_render

        elif self._is_papirus():
            logging.info("initializing papirus display")
            from pwnagotchi.ui.papirus.epd import EPD
            os.environ['EPD_SIZE'] = '2.0'
            self._display = EPD()
            self._display.clear()
            self._render_cb = self._papirus_render

        elif self._is_waveshare_v1():
            logging.info("initializing waveshare v1 display")
            from pwnagotchi.ui.waveshare.v1.epd2in13 import EPD
            self._display = EPD()
            self._display.init(self._display.lut_full_update)
            self._display.Clear(0xFF)
            self._display.init(self._display.lut_partial_update)
            self._render_cb = self._waveshare_render

        elif self._is_waveshare_v2():
            logging.info("initializing waveshare v2 display")
            from pwnagotchi.ui.waveshare.v2.waveshare import EPD
            self._display = EPD()
            self._display.init(self._display.FULL_UPDATE)
            self._display.Clear(WHITE)
            self._display.init(self._display.PART_UPDATE)
            self._render_cb = self._waveshare_render

        else:
            logging.critical("unknown display type %s" % self._display_type)

        plugins.on('display_setup', self._display)

        self.on_render(self._on_view_rendered)

    def clear(self):
        if self._display is None:
            logging.error("no display object created")
        elif self._is_inky():
            self._display.Clear()
        elif self._is_papirus():
            self._display.clear()
        elif self._is_waveshare():
            self._display.Clear(WHITE)
        else:
            logging.critical("unknown display type %s" % self._display_type)

    def _inky_render(self):
        if self._display_color != 'mono':
            display_colors = 3
        else:
            display_colors = 2

        img_buffer = self._canvas.convert('RGB').convert('P', palette=1, colors=display_colors)
        if self._display_color == 'red':
            img_buffer.putpalette([
                255, 255, 255,  # index 0 is white
                0, 0, 0,  # index 1 is black
                255, 0, 0  # index 2 is red
            ])
        elif self._display_color == 'yellow':
            img_buffer.putpalette([
                255, 255, 255,  # index 0 is white
                0, 0, 0,  # index 1 is black
                255, 255, 0  # index 2 is yellow
            ])
        else:
            img_buffer.putpalette([
                255, 255, 255,  # index 0 is white
                0, 0, 0  # index 1 is black
            ])

        self._display.set_image(img_buffer)
        self._display.show()

    def _papirus_render(self):
        self._display.display(self._canvas)
        self._display.partial_update()

    def _waveshare_render(self):
        buf = self._display.getbuffer(self._canvas)
        if self._is_waveshare_v1():
            self._display.display(buf)
        elif self._is_waveshare_v2():
            self._display.displayPartial(buf)

    def image(self):
        img = None
        if self._canvas is not None:
            img = self._canvas if self._rotation == 0 else self._canvas.rotate(-self._rotation)
        return img

    def _on_view_rendered(self, img):
        VideoHandler.render(img)

        if self._enabled:
            self._canvas = (img if self._rotation == 0 else img.rotate(self._rotation))
            if self._render_cb is not None:
                self._render_cb()
