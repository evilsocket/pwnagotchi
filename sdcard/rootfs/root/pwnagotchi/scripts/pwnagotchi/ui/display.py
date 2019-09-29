import _thread
from threading import Lock

import io
import core
import pwnagotchi

from pwnagotchi.ui.view import WHITE, View

from http.server import BaseHTTPRequestHandler, HTTPServer


class VideoHandler(BaseHTTPRequestHandler):
    _lock = Lock()
    _buffer = None
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
            writer = io.BytesIO()
            img.save(writer, format='PNG')
            VideoHandler._buffer = writer.getvalue()

    def log_message(self, format, *args):
        return

    def _w(self, data):
        try:
            self.wfile.write(data)
        except:
            pass

    def do_GET(self):
        if self._buffer is None:
            self.send_response(404)

        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self._w(bytes(self._index % (pwnagotchi.name(), 1000), "utf8"))

        elif self.path.startswith('/ui'):
            with self._lock:
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.send_header('Content-length', '%d' % len(self._buffer))
                self.end_headers()
                self._w(self._buffer)
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
        self.full_refresh_count = 0
        self.full_refresh_trigger = config['ui']['display']['refresh'] 

        self._render_cb = None
        self._display = None
        self._httpd = None
        self.canvas = None

        if self._enabled:
            self._init_display()
        else:
            self.on_render(self._on_view_rendered)
            core.log("display module is disabled")

        if self._video_enabled:
            _thread.start_new_thread(self._http_serve, ())

    def _http_serve(self):
        if self._video_address is not None:
            self._httpd = HTTPServer((self._video_address, self._video_port), VideoHandler)
            core.log("ui available at http://%s:%d/" % (self._video_address, self._video_port))
            self._httpd.serve_forever()
        else:
            core.log("could not get ip of usb0, video server not starting")

    def _is_inky(self):
        return self._display_type in ('inkyphat', 'inky')

    def _is_waveshare1(self):
        return self._display_type in ('waveshare_1', 'ws_1', 'waveshare1', 'ws1')

    def _is_waveshare2(self):
        return self._display_type in ('waveshare_2', 'ws_2', 'waveshare2', 'ws2')

    def _init_display(self):
        if self._is_inky():
            from inky import InkyPHAT
            self._display = InkyPHAT(self._display_color)
            self._display.set_border(InkyPHAT.BLACK)
            self._render_cb = self._inky_render
        elif self._is_waveshare1():
            from pwnagotchi.ui.waveshare.v1.epd2in13 import EPD
            # core.log("display module started")
            self._display = EPD()
            self._display.init(self._display.lut_full_update)
            self._display.Clear(0xFF)
            self._display.init(self._display.lut_partial_update)
            self._render_cb = self._waveshare_render
        elif self._is_waveshare2():
            from pwnagotchi.ui.v2.waveshare import EPD
            # core.log("display module started")
            self._display = EPD()
            self._display.init(self._display.FULL_UPDATE)
            self._display.Clear(WHITE)
            self._display.init(self._display.PART_UPDATE)
            self._render_cb = self._waveshare_render
        else:
            core.log("unknown display type %s" % self._display_type)

        self.on_render(self._on_view_rendered)

        core.log("display type '%s' initialized (color:%s)" % (self._display_type, self._display_color))

    def image(self):
        img = None
        if self.canvas is not None:
            img = self.canvas if self._rotation == 0 else self.canvas.rotate(-self._rotation)
        return img

    def _inky_render(self):
        if self._display_color != 'mono':
            display_colors = 3
        else:
            display_colors = 2

        imgbuf = self.canvas.convert('RGB').convert('P', palette=1, colors=display_colors)

        if self._display_color == 'red':
            imgbuf.putpalette([
                255, 255, 255,  # index 0 is white
                0, 0, 0,  # index 1 is black
                255, 0, 0  # index 2 is red
            ])
        elif self._display_color == 'yellow':
            imgbuf.putpalette([
                255, 255, 255,  # index 0 is white
                0, 0, 0,  # index 1 is black
                255, 255, 0  # index 2 is yellow
            ])
        else:
            imgbuf.putpalette([
                255, 255, 255,  # index 0 is white
                0, 0, 0  # index 1 is black
            ])

        self._display.set_image(imgbuf)
        self._display.show()

    def _waveshare_render(self):
        buf = self._display.getbuffer(self.canvas)
        if self._is_waveshare1:
            if self.full_refresh_count == self.full_refresh_trigger:
                self._display.Clear(0x00)
            self._display.display(buf)
        elif self._is_waveshare2:
            if self.full_refresh_count == self.full_refresh_trigger:
                self._display.Clear(BLACK)
            self._display.displayPartial(buf)
        self._display.sleep()
        if self.full_refresh_count == self.full_refresh_trigger:
           self.full_refresh_count = 0
        else:
           self.full_refresh_count += 1

    def _on_view_rendered(self, img):
        # core.log("display::_on_view_rendered")
        VideoHandler.render(img)

        if self._enabled:
            self.canvas = img if self._rotation == 0 else img.rotate(self._rotation)
            if self._render_cb is not None:
                self._render_cb()
