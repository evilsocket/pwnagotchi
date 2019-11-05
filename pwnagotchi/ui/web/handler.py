import logging
import os
import _thread

# https://stackoverflow.com/questions/14888799/disable-console-messages-in-flask-server
logging.getLogger('werkzeug').setLevel(logging.ERROR)
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

import pwnagotchi
import pwnagotchi.ui.web as web
from pwnagotchi import plugins

from flask import send_file
from flask import request
from flask import abort
from flask import render_template, render_template_string


class Handler:
    def __init__(self, agent, app):
        self._agent = agent
        self._app = app
        self._app.add_url_rule('/', 'index', self.index)
        self._app.add_url_rule('/ui', 'ui', self.ui)
        self._app.add_url_rule('/shutdown', 'shutdown', self.shutdown, methods=['POST'])
        self._app.add_url_rule('/restart', 'restart', self.restart, methods=['POST'])
        # plugins
        self._app.add_url_rule('/plugins', 'plugins', self.plugins, strict_slashes=False,
                               defaults={'name': None, 'subpath': None})
        self._app.add_url_rule('/plugins/<name>', 'plugins', self.plugins, strict_slashes=False,
                               methods=['GET', 'POST'], defaults={'subpath': None})
        self._app.add_url_rule('/plugins/<name>/<path:subpath>', 'plugins', self.plugins, methods=['GET', 'POST'])

    def index(self):
        return render_template('index.html', title=pwnagotchi.name(),
                               other_mode='AUTO' if self._agent.mode == 'manual' else 'MANU')

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
                return render_template_string(
                    plugins.loaded[name].on_webhook(subpath, args=arguments, req_method=req_method))

            abort(500)

    # serve a message and shuts down the unit
    def shutdown(self):
        try:
            return render_template('status.html', title=pwnagotchi.name(), go_back_after=60,
                                   message='Shutting down ...')
        finally:
            _thread.start_new_thread(pwnagotchi.shutdown, ())

    # serve a message and restart the unit in the other mode
    def restart(self):
        mode = request.form['mode']
        if mode not in ('AUTO', 'MANU'):
            mode = 'MANU'

        try:
            return render_template('status.html', title=pwnagotchi.name(), go_back_after=30,
                                   message='Restarting in %s mode ...' % mode)
        finally:
            _thread.start_new_thread(pwnagotchi.restart, (mode,))

    # serve the PNG file with the display image
    def ui(self):
        with web.frame_lock:
            return send_file(web.frame_path, mimetype='image/png')
