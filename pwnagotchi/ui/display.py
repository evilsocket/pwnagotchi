import _thread
from threading import Lock

import shutil
import logging
import os
import pwnagotchi, pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts

from pwnagotchi.ui.view import WHITE, View

from http.server import BaseHTTPRequestHandler, HTTPServer


class InkyPhatDisplay:
    def __init__(self):
        self._display = None
        self._display_color = 'black'

    def is_applicable(self, display_type):
        return display_type in ('inkyphat', 'inky')

    def create(self, display_color):
        logging.info("initializing inky display")
        self._display_color = display_color
        from inky import InkyPHAT
        self._display = InkyPHAT(display_color)
        self._display.set_border(InkyPHAT.BLACK)

    def get_display_specifics(self):
        fonts.setup(10, 8, 10, 25)

        width = 212
        height = 104
        face_pos = (0, int(height / 4))
        name_pos = (5, int(height * .15))
        status_pos = (int(width / 2) - 15, int(height * .15))

        return width, height, face_pos, name_pos, status_pos

    def get_display(self):
        return self._display

    def clear(self):
        self._display.Clear()

    def render(self, canvas):
        if self._display_color != 'mono':
            display_colors = 3
        else:
            display_colors = 2

        img_buffer = canvas.convert('RGB').convert('P', palette=1, colors=display_colors)

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
        try:
            self._display.show()
        except:
            print("")


class PapirusDisplay:
    def __init__(self):
        self._display = None

    def is_applicable(self, display_type):
        return display_type in ('papirus', 'papi')

    def create(self, display_color):
        logging.info("initializing papirus display")
        from pwnagotchi.ui.papirus.epd import EPD
        os.environ['EPD_SIZE'] = '2.0'
        self._display = EPD()
        self._display.clear()

    def get_display_specifics(self):
        fonts.setup(10, 8, 10, 23)

        width = 200
        height = 96
        face_pos = (0, int(height / 4))
        name_pos = (5, int(height * .15))
        status_pos = (int(width / 2) - 15, int(height * .15))

        return width, height, face_pos, name_pos, status_pos

    def get_display(self):
        return self._display

    def clear(self):
        self._display.clear()

    def render(self, canvas):
        self._display.display(canvas)
        self._display.partial_update()


class WaveShare1Display:
    def __init__(self):
        self._display = None

    def is_applicable(self, display_type):
        return display_type in ('waveshare_1', 'ws_1', 'waveshare1', 'ws1')

    def create(self, display_color):
        logging.info("initializing waveshare v1 display")
        from pwnagotchi.ui.waveshare.v1.epd2in13 import EPD
        self._display = EPD()
        self._display.init(self._display.lut_full_update)
        self._display.Clear(0xFF)
        self._display.init(self._display.lut_partial_update)

    def get_display_specifics(self):
        fonts.setup(10, 9, 10, 35)

        width = 250
        height = 122
        face_pos = (0, 40)
        name_pos = (5, 20)
        status_pos = (125, 20)

        return width, height, face_pos, name_pos, status_pos

    def get_display(self):
        return self._display

    def clear(self):
        self._display.Clear(WHITE)

    def render(self, canvas):
        buf = self._display.getbuffer(canvas)
        self._display.display(buf)
        pass


class WaveShare2Display:
    def __init__(self):
        self._display = None

    def is_applicable(self, display_type):
        return display_type in ('waveshare_2', 'ws_2', 'waveshare2', 'ws2')

    def create(self, display_color):
        logging.info("initializing waveshare v2 display")
        from pwnagotchi.ui.waveshare.v2.waveshare import EPD
        self._display = EPD()
        self._display.init(self._display.FULL_UPDATE)
        self._display.Clear(WHITE)
        self._display.init(self._display.PART_UPDATE)

    def get_display_specifics(self):
        fonts.setup(10, 9, 10, 35)

        width = 250
        height = 122
        face_pos = (0, 40)
        name_pos = (5, 20)
        status_pos = (125, 20)
        return width, height, face_pos, name_pos, status_pos

    def get_display(self):
        return self._display

    def clear(self):
        self._display.Clear(WHITE)

    def render(self, canvas):
        logging.info("rendering waveshare v2 display")
        buf = self._display.getbuffer(canvas)
        self._display.displayPartial(buf)
        pass


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


class Display:
    def __init__(self, config):
        self._enabled = config['ui']['display']['enabled']
        self._rotation = config['ui']['display']['rotation']
        self._video_enabled = config['ui']['display']['video']['enabled']
        self._video_port = config['ui']['display']['video']['port']
        self._video_address = config['ui']['display']['video']['address']
        self._display_type = config['ui']['display']['type']
        self._display_color = config['ui']['display']['color']
        self._display = None
        self._httpd = None

        self.available_renderers = [
            WaveShare1Display(),
            WaveShare2Display(),
            PapirusDisplay(),
            InkyPhatDisplay()
        ]

        self._renderer = None

        if self._enabled:
            self._init_display(self._display_type)
        else:
            self.clear()
            logging.warning("display module is disabled")

        logging.info("video_enabled = {%s}" % self._video_enabled)

        if self._video_enabled:
            _thread.start_new_thread(self._http_serve, ())

    def _http_serve(self):
        if self._video_address is not None:
            logging.info("Creating HttpServer {%s} {%s}" % (self._video_address, self._video_port))
            self._httpd = HTTPServer((self._video_address, self._video_port), VideoHandler)
            logging.info("ui available at http://%s:%d/" % (self._video_address, self._video_port))
            self._httpd.serve_forever()
        else:
            logging.info("could not get ip of usb0, video server not starting")

    def _init_display(self, display_type):
        for renderer in self.available_renderers:
            if renderer.is_applicable(display_type):
                self._renderer = renderer
                self._renderer.create(self._display_color)
                break

        if self._renderer is None:
            logging.critical("unknown display type %s" % self._display_type)

        plugins.on('display_setup', self._renderer.get_display())

    def _prepare_image(self, canvas):
        img = None
        if canvas is not None:
            img = canvas if self._rotation == 0 else canvas.rotate(-self._rotation)

        return img

    def get_specifics(self):
        if self._renderer is None:
            logging.error("no display object created")

        return self._renderer.get_display_specifics()

    def clear(self):
        if self._renderer is None:
            logging.error("no display object created")

        self._renderer.clear()

    def render(self, canvas):
        VideoHandler.render(canvas)

        img = self._prepare_image(canvas)
        if self._enabled and self._renderer is not None:
            self._renderer.render(img)
