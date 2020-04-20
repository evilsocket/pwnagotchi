import pwnagotchi.plugins as plugins
import logging
import os
import json
import re
import datetime
from flask import Response
from functools import lru_cache
from dateutil.parser import parse

'''
    webgpsmap shows existing position data stored in your /handshakes/ directory

    the plugin does the following:
        - search for *.pcap files in your /handshakes/ dir
            - for every found .pcap file it looks for a .geo.json or .gps.json or .paw-gps.json file with
              latitude+longitude data inside and shows this position on the map
            - if also an .cracked file with a plaintext password inside exist, it reads the content and shows the
              position as green instead of red and the password inside the infopox of the position
    special:
        you can save the html-map as one file for offline use or host on your own webspace with "/plugins/webgpsmap/offlinemap"

'''

class Webgpsmap(plugins.Plugin):
    __author__ = 'https://github.com/xenDE and https://github.com/dadav'
    __version__ = '1.4.0'
    __name__ = 'webgpsmap'
    __license__ = 'GPL3'
    __description__ = 'a plugin for pwnagotchi that shows a openstreetmap with positions of ap-handshakes in your webbrowser'

    ALREADY_SENT = list()
    SKIP = list()

    def __init__(self):
        self.ready = False

    def on_config_changed(self, config):
        self.config = config
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
        response_header_contentdisposition = None
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
                logging.error(f"[webgpsmap] on_webhook NOT_READY error: {error}")
                return
        else:
            if request.method == "GET":
                if path == '/' or not path:
                    # returns the html template
                    self.ALREADY_SENT = list()
                    try:
                        response_data = bytes(self.get_html(), "utf-8")
                    except Exception as error:
                        logging.error(f"[webgpsmap] on_webhook / error: {error}")
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
                        logging.error(f"[webgpsmap] on_webhook all error: {error}")
                        return
                elif path.startswith('offlinemap'):
                    # for download an all-in-one html file with positions.json inside
                    try:
                        self.ALREADY_SENT = list()
                        json_data = json.dumps(self.load_gps_from_dir(self.config['bettercap']['handshakes']))
                        html_data = self.get_html()
                        html_data = html_data.replace('var positions = [];', 'var positions = ' + json_data + ';positionsLoaded=true;drawPositions();')
                        response_data = bytes(html_data, "utf-8")
                        response_status = 200
                        response_mimetype = "application/xhtml+xml"
                        response_header_contenttype = 'text/html'
                        response_header_contentdisposition = 'attachment; filename=webgpsmap.html';
                    except Exception as error:
                        logging.error(f"[webgpsmap] on_webhook offlinemap: error: {error}")
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
                    <body>4😋4 for bad boys</body>
                    </html>''', "utf-8")
                response_status = 404
        try:
            r = Response(response=response_data, status=response_status, mimetype=response_mimetype)
            if response_header_contenttype is not None:
                r.headers["Content-Type"] = response_header_contenttype
            if response_header_contentdisposition is not None:
                r.headers["Content-Disposition"] = response_header_contentdisposition
            return r
        except Exception as error:
            logging.error(f"[webgpsmap] on_webhook CREATING_RESPONSE error: {error}")
            return

    # cache 2048 items
    @lru_cache(maxsize=2048, typed=False)
    def _get_pos_from_file(self, path):
        return PositionFile(path)


    def load_gps_from_dir(self, gpsdir, newest_only=False):
        """
        Parses the gps-data from disk
        """

        handshake_dir = gpsdir
        gps_data = dict()

        logging.info(f"[webgpsmap] scanning {handshake_dir}")


        all_files = os.listdir(handshake_dir)
        #print(all_files)
        all_pcap_files = [os.path.join(handshake_dir, filename)
                                for filename in all_files
                                if filename.endswith('.pcap')
                                ]
        all_geo_or_gps_files = []
        for filename_pcap in all_pcap_files:
            filename_base = filename_pcap[:-5]  # remove ".pcap"
            logging.debug(f"[webgpsmap] found: {filename_base}")
            filename_position = None

            logging.debug("[webgpsmap] search for .gps.json")
            check_for = os.path.basename(filename_base) + ".gps.json"
            if check_for in all_files:
                filename_position = str(os.path.join(handshake_dir, check_for))

            logging.debug("[webgpsmap] search for .geo.json")
            check_for = os.path.basename(filename_base) + ".geo.json"
            if check_for in all_files:
                filename_position = str(os.path.join(handshake_dir, check_for))

            logging.debug("[webgpsmap] search for .paw-gps.json")
            check_for = os.path.basename(filename_base) + ".paw-gps.json"
            if check_for in all_files:
                filename_position = str(os.path.join(handshake_dir, check_for))

            logging.debug(f"[webgpsmap] end search for position data files and use {filename_position}")

            if filename_position is not None:
                all_geo_or_gps_files.append(filename_position)

    #    all_geo_or_gps_files = set(all_geo_or_gps_files) - set(SKIP)   # remove skipped networks? No!

        if newest_only:
            all_geo_or_gps_files = set(all_geo_or_gps_files) - set(self.ALREADY_SENT)

        logging.info(f"[webgpsmap] Found {len(all_geo_or_gps_files)} position-data files from {len(all_pcap_files)} handshakes. Fetching positions ...")

        for pos_file in all_geo_or_gps_files:
            try:
                pos = self._get_pos_from_file(pos_file)
                if not pos.type() == PositionFile.GPS and not pos.type() == PositionFile.GEO and not pos.type() == PositionFile.PAWGPS:
                    continue

                ssid, mac = pos.ssid(), pos.mac()
                ssid = "unknown" if not ssid else ssid
                # invalid mac is strange and should abort; ssid is ok
                if not mac:
                    raise ValueError("Mac can't be parsed from filename")
                pos_type = 'unknown'
                if pos.type() == PositionFile.GPS:
                    pos_type = 'gps'
                elif pos.type() == PositionFile.GEO:
                    pos_type = 'geo'
                elif pos.type() == PositionFile.PAWGPS:
                    pos_type = 'paw'
                gps_data[ssid+"_"+mac] = {
                    'ssid': ssid,
                    'mac': mac,
                    'type': pos_type,
                    'lng': pos.lng(),
                    'lat': pos.lat(),
                    'acc': pos.accuracy(),
                    'ts_first': pos.timestamp_first(),
                    'ts_last': pos.timestamp_last(),
                    }

                # get ap password if exist
                check_for = os.path.basename(pos_file).split(".")[0] + ".pcap.cracked"
                if check_for in all_files:
                    gps_data[ssid + "_" + mac]["pass"] = pos.password()

                self.ALREADY_SENT += pos_file
            except json.JSONDecodeError as error:
                self.SKIP += pos_file
                logging.error(f"[webgpsmap] JSONDecodeError in: {pos_file} - error: {error}")
                continue
            except ValueError as error:
                self.SKIP += pos_file
                logging.error(f"[webgpsmap] ValueError: {pos_file} - error: {error}")
                continue
            except OSError as error:
                self.SKIP += pos_file
                logging.error(f"[webgpsmap] OSError: {pos_file} - error: {error}")
                continue
        logging.info(f"[webgpsmap] loaded {len(gps_data)} positions")
        return gps_data

    def get_html(self):
        """
        Returns the html page
        """
        try:
            template_file = os.path.dirname(os.path.realpath(__file__)) + "/" + "webgpsmap.html"
            html_data = open(template_file, "r").read()
        except Exception as error:
            logging.error(f"[webgpsmap] error loading template file {template_file} - error: {error}")
        return html_data


class PositionFile:
    """
    Wraps gps / net-pos files
    """
    GPS = 1
    GEO = 2
    PAWGPS = 3

    def __init__(self, path):
        self._file = path
        self._filename = os.path.basename(path)
        try:
            logging.debug(f"[webgpsmap] loading {path}")
            with open(path, 'r') as json_file:
                self._json = json.load(json_file)
            logging.debug(f"[webgpsmap] loaded {path}")
        except json.JSONDecodeError as js_e:
            raise js_e

    def mac(self):
        """
        Returns the mac from filename
        """
        parsed_mac = re.search(r'.*_?([a-zA-Z0-9]{12})\.(?:gps|geo|paw-gps)\.json', self._filename)
        if parsed_mac:
            mac = parsed_mac.groups()[0]
            return mac
        return None

    def ssid(self):
        """
        Returns the ssid from filename
        """
        parsed_ssid = re.search(r'(.+)_[a-zA-Z0-9]{12}\.(?:gps|geo|paw-gps)\.json', self._filename)
        if parsed_ssid:
            return parsed_ssid.groups()[0]
        return None


    def json(self):
        """
        returns the parsed json
        """
        return self._json

    def timestamp_first(self):
        """
        returns the timestamp of AP first seen
        """
        # use file timestamp creation time of the pcap file
        return int("%.0f" % os.path.getctime(self._file))

    def timestamp_last(self):
        """
        returns the timestamp of AP last seen
        """
        return_ts = None
        if 'ts' in self._json:
            return_ts = self._json['ts']
        elif 'Updated' in self._json:
            # convert gps datetime to unix timestamp: "2019-10-05T23:12:40.422996+01:00"
            dateObj = parse(self._json['Updated'])
            return_ts = int("%.0f" % dateObj.timestamp())
        else:
            # use file timestamp last modification of the json file
            return_ts = int("%.0f" % os.path.getmtime(self._file))
        return return_ts

    def password(self):
        """
        returns the password from file.pcap.cracked or None
        """
        return_pass = None
        # 2do: make better filename split/remove extension because this one has problems with "." in path
        base_filename, ext1, ext2 = re.split('\.', self._file)
        password_file_path = base_filename + ".pcap.cracked"
        if os.path.isfile(password_file_path):
            try:
                password_file = open(password_file_path, 'r')
                return_pass = password_file.read()
                password_file.close()
            except OSError as error:
                logging.error(f"[webgpsmap] OS error loading password: {password_file_path} - error: {format(error)}")
            except:
                logging.error(f"[webgpsmap] Unexpected error loading password: {password_file_path} - error: {sys.exc_info()[0]}")
                raise
        return return_pass

    def type(self):
        """
        returns the type of the file
        """
        if self._file.endswith('.gps.json'):
            return PositionFile.GPS
        if self._file.endswith('.geo.json'):
            return PositionFile.GEO
        if self._file.endswith('.paw-gps.json'):
            return PositionFile.PAWGPS
        return None

    def lat(self):
        try:
            lat = None
            # try to get value from known formats
            if 'Latitude' in self._json:
                lat = self._json['Latitude']
            if 'lat' in self._json:
                lat = self._json['lat']  # an old paw-gps format: {"long": 14.693561, "lat": 40.806375}
            if 'location' in self._json:
                if 'lat' in self._json['location']:
                    lat = self._json['location']['lat']
            # check value
            if lat is None:
                raise ValueError(f"Lat is None in {self._filename}")
            if lat == 0:
                raise ValueError(f"Lat is 0 in {self._filename}")
            return lat
        except KeyError:
            pass
        return None

    def lng(self):
        try:
            lng = None
            # try to get value from known formats
            if 'Longitude' in self._json:
                lng = self._json['Longitude']
            if 'long' in self._json:
                lng = self._json['long']  # an old paw-gps format: {"long": 14.693561, "lat": 40.806375}
            if 'location' in self._json:
                if 'lng' in self._json['location']:
                    lng = self._json['location']['lng']
            # check value
            if lng is None:
                raise ValueError(f"Lng is None in {self._filename}")
            if lng == 0:
                raise ValueError(f"Lng is 0 in {self._filename}")
            return lng
        except KeyError:
            pass
        return None

    def accuracy(self):
        if self.type() == PositionFile.GPS:
            return 50.0 # a default
        if self.type() == PositionFile.PAWGPS:
            return 50.0 # a default
        if self.type() == PositionFile.GEO:
            try:
                return self._json['accuracy']
            except KeyError:
                pass
        return None
