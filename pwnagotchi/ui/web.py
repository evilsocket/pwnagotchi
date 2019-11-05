import re
import _thread
import secrets
from threading import Lock
import shutil
import logging

import pwnagotchi
from pwnagotchi.agent import Agent
from pwnagotchi import plugins
from flask import Flask
from flask import send_file
from flask import request
from flask import abort
from flask import render_template_string
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect

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
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
        </form>
        <form style="display:inline;" method="POST" action="/restart" onsubmit="return confirm('This will restart the service in %s mode, continue?');">
            <input style="display:inline;" type="submit" class="block" value="Restart in %s mode"/>
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
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


class RequestHandler:
    def __init__(self, app):
        self._app = app
        self._app.add_url_rule('/', 'index', self.index)
        self._app.add_url_rule('/ui', 'ui', self.ui)
        self._app.add_url_rule('/shutdown', 'shutdown', self.shutdown, methods=['POST'])
        self._app.add_url_rule('/restart', 'restart', self.restart, methods=['POST'])
        # plugins
        self._app.add_url_rule('/plugins', 'plugins', self.plugins, strict_slashes=False, defaults={'name': None, 'subpath': None})
        self._app.add_url_rule('/plugins/<name>', 'plugins', self.plugins, strict_slashes=False, methods=['GET','POST'], defaults={'subpath': None})
        self._app.add_url_rule('/plugins/<name>/<path:subpath>', 'plugins', self.plugins, methods=['GET','POST'])


    def index(self):
        other_mode = 'AUTO' if Agent.INSTANCE.mode == 'manual' else 'MANU'
        return render_template_string(INDEX % (
            pwnagotchi.name(),
            other_mode,
            other_mode,
            1000))

    def plugins(self, name, subpath):
        if name is None:
            # show plugins overview
            abort(404)
        else:

            # call plugin on_webhook
            arguments = request.args
            req_method = request.method

            # need to return something here
            if name in plugins.loaded and hasattr(plugins.loaded[name], 'on_webhook'):
                return render_template_string(plugins.loaded[name].on_webhook(subpath, args=arguments, req_method=req_method))

            abort(500)


    # serve a message and shuts down the unit
    def shutdown(self):
        pwnagotchi.shutdown()
        return render_template_string(STATUS_PAGE % (pwnagotchi.name(), 'Shutting down ...'))

    # serve a message and restart the unit in the other mode
    def restart(self):
        other_mode = 'AUTO' if Agent.INSTANCE.mode == 'manual' else 'MANU'
        pwnagotchi.restart(other_mode)
        return render_template_string(STATUS_PAGE % (pwnagotchi.name(), 'Restart in %s mode ...' % other_mode))

    # serve the PNG file with the display image
    def ui(self):
        global frame_lock, frame_path

        with frame_lock:
            return send_file(frame_path, mimetype='image/png')


class Server:
    def __init__(self, config):
        self._enabled = config['video']['enabled']
        self._port = config['video']['port']
        self._address = config['video']['address']
        self._origin = None

        if 'origin' in config['video']:
            self._origin = config['video']['origin']

        if self._enabled:
            _thread.start_new_thread(self._http_serve, ())

    def _http_serve(self):
        if self._address is not None:
            app = Flask(__name__)
            app.secret_key = secrets.token_urlsafe(256)

            if self._origin:
                CORS(app, resources={r"*": {"origins": self._origin}})

            CSRFProtect(app)
            RequestHandler(app)

            app.run(host=self._address, port=self._port, debug=False)
        else:
            logging.info("could not get ip of usb0, video server not starting")
