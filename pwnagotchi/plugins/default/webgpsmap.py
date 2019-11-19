import pwnagotchi.plugins as plugins
import logging
import os
import json
import re
import datetime
from flask import Response
from functools import lru_cache

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
    - 
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
        logging.info("webgpsmap plugin loaded")

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
            except Exception as ex:
                logging.error(ex)
                return
        else:
            if request.method == "GET":
                if path == '/' or not path:
                    # returns the html template
                    self.ALREADY_SENT = list()
                    try:
                        response_data = bytes(self.get_html(), "utf-8")
                    except Exception as ex:
                        logging.error(ex)
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
                    except Exception as ex:
                        logging.error(ex)
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
        except Exception as ex:
            logging.error(ex)
            return

    # cache 1024 items
    @lru_cache(maxsize=1024, typed=False)
    def _get_pos_from_file(self, path):
        return PositionFile(path)


    def load_gps_from_dir(self, gpsdir, newest_only=False):
        """
        Parses the gps-data from disk
        """

        handshake_dir = gpsdir
        gps_data = dict()

        logging.info("webgpsmap: scanning %s", handshake_dir)


        all_files = os.listdir(handshake_dir)
        #print(all_files)
        all_pcap_files = [os.path.join(handshake_dir, filename)
                                for filename in all_files
                                if filename.endswith('.pcap')
                                ]
        all_geo_or_gps_files = []
        for filename_pcap in all_pcap_files:
            filename_base = filename_pcap[:-5]  # remove ".pcap"
            logging.debug("webgpsmap: found: " + filename_base)
            filename_position = None

            check_for = os.path.basename(filename_base) + ".gps.json"
            if check_for in all_files:
                filename_position = str(os.path.join(handshake_dir, check_for))

            check_for = os.path.basename(filename_base) + ".geo.json"
            if check_for in all_files:
                filename_position = str(os.path.join(handshake_dir, check_for))

            if filename_position is not None:
    #            logging.debug("webgpsmap: -- found: %s %d" % (check_for, len(all_geo_or_gps_files)) )
                all_geo_or_gps_files.append(filename_position)

    #    all_geo_or_gps_files = set(all_geo_or_gps_files) - set(SKIP)   # remove skiped networks? No!

        if newest_only:
            all_geo_or_gps_files = set(all_geo_or_gps_files) - set(self.ALREADY_SENT)

        logging.info("webgpsmap: Found %d .(geo|gps).json files from %d handshakes. Fetching positions ...",
                     len(all_geo_or_gps_files), len(all_pcap_files))

        for pos_file in all_geo_or_gps_files:
            try:
                pos = self._get_pos_from_file(pos_file)
                if not pos.type() == PositionFile.GPS and not pos.type() == PositionFile.GEO:
                    continue

                ssid, mac = pos.ssid(), pos.mac()
                ssid = "unknown" if not ssid else ssid
                # invalid mac is strange and should abort; ssid is ok
                if not mac:
                    raise ValueError("Mac can't be parsed from filename")
                gps_data[ssid+"_"+mac] = {
                    'ssid': ssid,
                    'mac': mac,
                    'type': 'gps' if pos.type() == PositionFile.GPS else 'geo',
                    'lng': pos.lng(),
                    'lat': pos.lat(),
                    'acc': pos.accuracy(),
                    'ts_first': pos.timestamp_first(),
                    'ts_last': pos.timestamp_last(),
                    }

                check_for = os.path.basename(pos_file[:-9]) + ".pcap.cracked"
                if check_for in all_files:
                    gps_data[ssid + "_" + mac]["pass"] = pos.password()

                self.ALREADY_SENT += pos_file
            except json.JSONDecodeError as js_e:
                self.SKIP += pos_file
                logging.error(js_e)
                continue
            except ValueError as v_e:
                self.SKIP += pos_file
                logging.error(v_e)
                continue
            except OSError as os_e:
                self.SKIP += pos_file
                logging.error(os_e)
                continue
        logging.info("webgpsmap loaded %d positions", len(gps_data))
        return gps_data

    def get_html(self):
        """
        Returns the html page
        """
        try:
            template_file = os.path.dirname(os.path.realpath(__file__))+"/"+"webgpsmap.html"
            html_data = open(template_file, "r").read()
        except Exception as ex:
            logging.error("error loading template file: %s", template_file)
            logging.error(ex)
        return html_data


class PositionFile:
    """
    Wraps gps / net-pos files
    """
    GPS = 0
    GEO = 1

    def __init__(self, path):
        self._file = path
        self._filename = os.path.basename(path)
        try:
            with open(path, 'r') as json_file:
                self._json = json.load(json_file)
        except json.JSONDecodeError as js_e:
            raise js_e

    def mac(self):
        """
        Returns the mac from filename
        """
        parsed_mac = re.search(r'.*_?([a-zA-Z0-9]{12})\.(?:gps|geo)\.json', self._filename)
        if parsed_mac:
            mac = parsed_mac.groups()[0]
            return mac
        return None

    def ssid(self):
        """
        Returns the ssid from filename
        """
        parsed_ssid = re.search(r'(.+)_[a-zA-Z0-9]{12}\.(?:gps|geo)\.json', self._filename)
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
            date_iso_formated = self._json['Updated']
            # fill/cut microseconds to 6 numbers
            part1, part2, part3 = re.split('\.|\+', date_iso_formated)
            part2 = part2.ljust(6, '0')[:6]
            date_iso_formated = part1 + "." + part2 + "+" + part3
            dateObj = datetime.datetime.fromisoformat(date_iso_formated)
            return_ts = int("%.0f" % dateObj.timestamp())
        else:
            # use file timestamp last modification of the pcap file
            return_ts = int("%.0f" % os.path.getmtime(self._file))
        return return_ts

    def password(self):
        """
        returns the password from file.pcap.cracked od None
        """
        return_pass = None
        password_file_path = self._file[:-9] + ".pcap.cracked"
        if os.path.isfile(password_file_path):
            try:
                password_file = open(password_file_path, 'r')
                return_pass = password_file.read()
                password_file.close()
            except OSError as err:
                print("OS error: {0}".format(err))
            except:
                print("Unexpected error:", sys.exc_info()[0])
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
        return None

    def lat(self):
        try:
            if self.type() == PositionFile.GPS:
                lat = self._json['Latitude']
            if self.type() == PositionFile.GEO:
                lat = self._json['location']['lat']
            if lat != 0:
                return lat
            raise ValueError("Lat is 0")
        except KeyError:
            pass
        return None

    def lng(self):
        try:
            if self.type() == PositionFile.GPS:
                lng = self._json['Longitude']
            if self.type() == PositionFile.GEO:
                lng = self._json['location']['lng']
            if lng != 0:
                return lng
            raise ValueError("Lng is 0")
        except KeyError:
            pass
        return None

    def accuracy(self):
        if self.type() == PositionFile.GPS:
            return 50.0
        if self.type() == PositionFile.GEO:
            try:
                return self._json['accuracy']
            except KeyError:
                pass
        return None
