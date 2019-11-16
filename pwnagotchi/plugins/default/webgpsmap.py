import datetime
import json
import logging
import os
import re
from pathlib import Path

from dateutil import parser
from flask import Response

import pwnagotchi.plugins as plugins

'''
2do:
    - make the cache handling multiple clients
    - cleanup the javascript in a class and handle "/newest" additions
    - create map filters (only cracked APs, only last xx days, between 2 days with slider)
        http://www.gistechsolutions.com/leaflet/DEMO/filter/filter.html
        https://gis.stackexchange.com/questions/312737/filtering-interactive-leaflet-map-with-dropdown-menu
        https://blogs.kent.ac.uk/websolutions/2015/01/29/filtering-map-markers-with-leaflet-js-a-brief-technical-overview/
        http://www.digital-geography.com/filter-leaflet-maps-slider/
        http://bl.ocks.org/zross/47760925fcb1643b4225
'''


class Webgpsmap(plugins.Plugin):
    __author__ = 'https://github.com/xenDE and https://github.com/dadav'
    __version__ = '1.2.2'
    __name__ = 'webgpsmap'
    __license__ = 'GPL3'
    __description__ = 'a plugin for pwnagotchi that shows a openstreetmap with positions of ap-handshakes in your webbrowser'
    __help__ = """
- install: copy "webgpsmap.py" and "webgpsmap.html" to your configured "custom_plugins" directory
- add webgpsmap.yml to your config
- connect your PC/Smartphone/* with USB, BT or other to your pwnagotchi and browse to http://pwnagotchi.local:8080/plugins/webgpsmap/
  (change pwnagotchi.local to your pwnagotchis IP, if needed)
"""

    ALREADY_SENT = list()
    SKIP = list()

    def __init__(self):
        self.ready = False

    def on_ready(self, agent):
        self.config = agent.config()
        self.ready = True

    def on_loaded(self):
        """
        Plugin got loaded
        """
        logging.info("[webgpsmap]: plugin loaded")

    def on_webhook(self, path, request):
        """
        Returns ewquested data
        """
        # defaults:
        response_header_contenttype = None
        response_mimetype = "application/xhtml+xml"
        if not self.ready:
            try:
                response_data = bytes('''<html>
                    <head>
                    <meta charset="utf-8"/>
                    <style>body{font-size:1000%;}</style>
                    </head>
                    <body>Not ready yet</body>
                    </html>''', "utf-8")
                response_status = 500
                response_mimetype = "application/xhtml+xml"
                response_header_contenttype = 'text/html'
            except Exception as error:
                logging.error(f"[webgpsmap] error: {error}")
                return
        else:
            if request.method == "GET":
                if path == '/' or not path:
                    # returns the html template
                    self.ALREADY_SENT = list()
                    try:
                        response_data = bytes(self.get_html(), "utf-8")
                    except Exception as error:
                        logging.error(f"[webgpsmap] error: {error}")
                        return
                    response_status = 200
                    response_mimetype = "application/xhtml+xml"
                    response_header_contenttype = 'text/html'
                elif path.startswith('all'):
                    # returns all positions
                    try:
                        self.ALREADY_SENT = list()
                        response_data = bytes(json.dumps(self.load_gps_from_dir(self.config['bettercap']['handshakes'])), "utf-8")
                        response_status = 200
                        response_mimetype = "application/json"
                        response_header_contenttype = 'application/json'
                    except Exception as error:
                        logging.error(f"[webgpsmap] error: {error}")
                        return
                # elif path.startswith('/newest'):
                #     # returns all positions newer then timestamp
                #     response_data = bytes(json.dumps(self.load_gps_from_dir(self.config['bettercap']['handshakes']), newest_only=True), "utf-8")
                #     response_status = 200
                #     response_mimetype = "application/json"
                #     response_header_contenttype = 'application/json'
                else:
                    # unknown GET path
                    response_data = bytes('''<html>
                    <head>
                    <meta charset="utf-8"/>
                    <style>body{font-size:1000%;}</style>
                    </head>
                    <body>4😋4</body>
                    </html>''', "utf-8")
                    response_status = 404
            else:
                # unknown request.method
                response_data = bytes('''<html>
                    <head>
                    <meta charset="utf-8"/>
                    <style>body{font-size:1000%;}</style>
                    </head>
                    <body>4😋4</body>
                    </html>''', "utf-8")
                response_status = 404
        try:
            r = Response(response=response_data, status=response_status, mimetype=response_mimetype)
            if response_header_contenttype is not None:
                r.headers["Content-Type"] = response_header_contenttype
            return r
        except Exception as error:
            logging.error(f"[webgpsmap] error: {error}")
            return

    # # cache 1024 items
    # @lru_cache(maxsize=1024, typed=False)
    # def _get_pos_from_file(self, path):
    #     return PositionFile(path)

    def load_gps_from_dir(self, handshake_dir, newest_only=False):
        """
        Parses the gps-data from disk
        """
        try:
            handshakes_path = Path(handshake_dir)
            location_file_pattern = "*_*.g??.json"
            location_files = handshakes_path.glob(location_file_pattern)
            # handshake_files = handshakes_path.glob("/*_*.pcap")
        except Exception as error:
            logging.error(f"[webgpsmap] error: {error}")

        logging.info(f"[webgpsmap]: parsing files matching '{location_file_pattern}' in {handshakes_path}")

        locations = dict()

        for file_path in location_files:
            location_data = dict()

            logging.debug(f"[webgpsmap]: processing file {file_path.name}...")

            with open(file_path, 'r') as json_file:
                location_data = json.load(json_file)

            matches = re.search(r"(.*)_([a-zA-Z0-9]{12})\.(geo|gps)\.json", file_path.name)
            if matches and all([location_data["Longitude"], location_data["Latitude"]]):
                location_data["ssid"] = matches.group(1)
                location_data["mac"] = matches.group(2)
                location_data["source_type"] = matches.group(3)

                location_data["seen_first"] = os.path.getctime(file_path)
                location_data["seen_last"] = parser.isoparse(
                    location_data['Updated']).replace(tzinfo=datetime.timezone.utc).timestamp()

                # the great matching-the-html/js-part-hack
                location_data["lng"] = location_data["Longitude"]
                location_data["lat"] = location_data["Latitude"]
                location_data["type"] = location_data["source_type"]
                location_data["acc"] = location_data.get("accuracy", 0.0)
                location_data["ts_first"] = int(location_data['seen_first'])
                location_data["ts_last"] = int(location_data['seen_last'])

                net_id = "_".join([location_data["ssid"], location_data["mac"]])
                locations[net_id] = location_data

                logging.debug(f"[webgpsmap]: {file_path.name}: {locations[net_id]}")

        logging.info(f"[webgpsmap]: successfully loaded {len(locations)} locations")

        return locations

    def get_html(self):
        """
        Returns the html page
        """
        try:
            template_file = os.path.dirname(os.path.realpath(__file__)) + "/" + "webgpsmap.html"
            html_data = open(template_file, "r").read()
        except Exception as error:
            logging.error(f"[webgpsmap] error: loading template file {template_file}: {error}")
        return html_data
