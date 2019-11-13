import logging
import os
import _thread

# https://stackoverflow.com/questions/14888799/disable-console-messages-in-flask-server
logging.getLogger('werkzeug').setLevel(logging.ERROR)
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

import pwnagotchi
import pwnagotchi.ui.web as web
import pwnagotchi.grid as grid
from pwnagotchi import plugins

from flask import send_file
from flask import request
from flask import jsonify
from flask import abort
from flask import render_template, render_template_string


class Handler:
    def __init__(self, agent, app):
        self._agent = agent
        self._app = app
        self._app.add_url_rule('/', 'index', self.index)
        self._app.add_url_rule('/state/', 'state', self.state, defaults={'format': 'json'}, methods=['GET'])
        self._app.add_url_rule('/state/<format>', 'state', self.state, methods=['GET'])
        self._app.add_url_rule('/shutdown', 'shutdown', self.shutdown, methods=['POST'])
        self._app.add_url_rule('/restart', 'restart', self.restart, methods=['POST'])

        # plugins
        self._app.add_url_rule('/plugins', 'plugins', self.plugins, strict_slashes=False,
                               defaults={'name': None, 'subpath': None})
        self._app.add_url_rule('/plugins/<name>', 'plugins', self.plugins, strict_slashes=False,
                               methods=['GET', 'POST'], defaults={'subpath': None})
        self._app.add_url_rule('/plugins/<name>/<path:subpath>', 'plugins', self.plugins, methods=['GET', 'POST'])

    def _return_json(self):

        display = self._agent.view()

        mesh_data = grid.call("/mesh/data")
        mesh_peers = grid.peers()
        messages = grid.inbox()

        total_messages = len(messages)
        unread_messages = len([m for m in messages if m['seen_at'] is None])

        peers = []
        for peer in mesh_peers:
            peers.append({
                "identity": peer["advertisement"]["identity"],
                "name": peer["advertisement"]["name"],
                "face": peer["advertisement"]["face"],
                "pwnd_run": peer["advertisement"]["pwnd_run"],
                "pwnd_tot": peer["advertisement"]["pwnd_tot"],
            })

        result = {
            "identity": mesh_data["identity"],
            "epoch": mesh_data["epoch"],
            "status": display.get('status'),
            "channel_text": display.get('channel'),
            "aps_text": display.get('aps'),
            "apt_tot": self._agent.get_total_aps(),
            "aps_on_channel": self._agent.get_aps_on_channel(),
            "channel": self._agent.get_current_channel(),
            "uptime": display.get('uptime'),
            "mode": display.get('mode'),
            "name": mesh_data["name"],
            "face": mesh_data["face"],
            "num_peers": len(mesh_peers),
            "peers": peers,
            "total_messages": total_messages,
            "unread_messages": unread_messages,
            "friend_face_text": display.get('friend_face'),
            "friend_name_text": display.get('friend_name'),
            "pwnd_run": mesh_data["pwnd_run"],
            "pwnd_tot": mesh_data["pwnd_tot"],
            "version": pwnagotchi.version,
            "memory": pwnagotchi.mem_usage(),  # Scale 0-1
            "cpu": pwnagotchi.cpu_load(),  # Scale 0-1
            "temperature": pwnagotchi.temperature()  # Degrees C
        }

        return jsonify(result)

    def _return_png(self):
        # TODO - can we avoid writing to a file then reading, or keep it in memory?
        with web.frame_lock:
            return send_file(web.frame_path, mimetype="image/png")

    def index(self):

        theme = "theme-default.html"

        theme_config_location = self._agent.config()["ui"]["display"]["video"]

        if "theme" in theme_config_location:
            theme = "theme-" + theme_config_location["theme"] + ".html"

        return render_template(theme, title=pwnagotchi.name(),
                               other_mode='AUTO' if self._agent.mode == 'manual' else 'MANU')

    def state(self, format):
        if format not in ["json", "png"]:
            return abort(415)

        if format == "png":
            return self._return_png()

        return self._return_json()

    def plugins(self, name, subpath):
        if name is None:
            # show plugins overview
            abort(404)
        else:
            if name in plugins.loaded and hasattr(plugins.loaded[name], 'on_webhook'):
                try:
                    return plugins.loaded[name].on_webhook(subpath, request)
                except Exception:
                    abort(500)
            else:
                abort(404)

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

