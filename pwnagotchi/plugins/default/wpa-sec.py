import logging
import os
import re
import requests
import sqlite3
from datetime import datetime
from enum import Enum
from pwnagotchi import plugins
from pwnagotchi.utils import remove_whitelisted
from threading import Lock

class WpaSec(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '2.1.0'
    __license__ = 'GPL3'
    __description__ = 'This plugin automatically uploads handshakes to https://wpa-sec.stanev.org'
    
    class Status(Enum):
        TOUPLOAD = 0
        INVALID = 1
        SUCCESSFULL = 2

    def __init__(self):
        self.ready = False
        self.lock = Lock()
        
        self.options = dict()
        
        self._init_db()
        
    def _init_db(self):
        db_conn = sqlite3.connect('/root/.wpa_sec_db')
        db_conn.execute('pragma journal_mode=wal')
        with db_conn:
            db_conn.execute('''
                CREATE TABLE IF NOT EXISTS handshakes (
                    path TEXT PRIMARY KEY,
                    status INTEGER
                )
            ''')
            db_conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_handshakes_status
                ON handshakes (status)
            ''')
        db_conn.close()

    def on_loaded(self):
        """
        Gets called when the plugin gets loaded
        """
        if 'api_key' not in self.options or ('api_key' in self.options and not self.options['api_key']):
            logging.error("WPA_SEC: API-KEY isn't set. Can't upload.")
            return

        if 'api_url' not in self.options or ('api_url' in self.options and not self.options['api_url']):
            logging.error("WPA_SEC: API-URL isn't set. Can't upload.")
            return

        self.skip_until_reload = set()

        self.ready = True
        logging.info("WPA_SEC: plugin loaded.")
        
    def on_handshake(self, agent, filename, access_point, client_station):
        whitelist = self.options.get('whitelist', list())
        if not remove_whitelisted([filename], whitelist):
            return
        
        db_conn = sqlite3.connect('/root/.wpa_sec_db')
        with db_conn:
            db_conn.execute('''
                INSERT INTO handshakes (path, status)
                VALUES (?, ?)
                ON CONFLICT(path) DO UPDATE SET status = excluded.status
                WHERE handshakes.status = ?
            ''', (filename, self.Status.TOUPLOAD.value, self.Status.INVALID.value))
        db_conn.close()

    def on_internet_available(self, agent):
        """
        Called in manual mode when there's internet connectivity
        """
        if not self.ready or self.lock.locked():
            return

        with self.lock:
            display = agent.view()
            
            try:
                db_conn = sqlite3.connect('/root/.wpa_sec_db')
                cursor = db_conn.cursor()
                
                cursor.execute('SELECT path FROM handshakes WHERE status = ?', (self.Status.TOUPLOAD.value,))
                handshakes_toupload = [row[0] for row in cursor.fetchall()]
                handshakes_toupload = set(handshakes_toupload) - self.skip_until_reload

                if handshakes_toupload:
                    logging.info("WPA_SEC: Internet connectivity detected. Uploading new handshakes...")
                    for idx, handshake in enumerate(handshakes_toupload):
                        display.on_uploading(f"WPA-SEC ({idx + 1}/{len(handshakes_toupload)})")
                        logging.info("WPA_SEC: Uploading %s...", handshake)

                        try:
                            upload_response = self._upload_to_wpasec(handshake)
                            
                            if upload_response.startswith("hcxpcapngtool"):
                                logging.info(f"WPA_SEC: {handshake} successfully uploaded.")
                                new_status = self.Status.SUCCESSFULL.value
                            else:
                                logging.info(f"WPA_SEC: {handshake} uploaded, but it was invalid.")
                                new_status = self.Status.INVALID.value

                            cursor.execute('''
                                INSERT INTO handshakes (path, status)
                                VALUES (?, ?)
                                ON CONFLICT(path) DO UPDATE SET status = excluded.status
                            ''', (handshake, new_status))
                            db_conn.commit()
                            
                        except requests.exceptions.RequestException:
                            logging.exception("WPA_SEC: RequestException uploading %s, skipping until reload.", handshake)
                            self.skip_until_reload.append(handshake)
                        except OSError:
                            logging.exception("WPA_SEC: OSError uploading %s, deleting from db.", handshake)
                            cursor.execute('DELETE FROM handshakes WHERE path = ?', (handshake,))
                            db_conn.commit()
                        except Exception:
                            logging.exception("WPA_SEC: Exception uploading %s.", handshake)

                    display.on_normal()
                    
                cursor.close()
                db_conn.close()
            except Exception:
                logging.exception("WPA_SEC: Exception uploading results.")

            try:
                if 'download_results' in self.options and self.options['download_results']:
                    config = agent.config()
                    handshake_dir = config['bettercap']['handshakes']
                    
                    cracked_file_path = os.path.join(handshake_dir, 'wpa-sec.cracked.potfile')

                    if os.path.exists(cracked_file_path):
                        last_check = datetime.fromtimestamp(os.path.getmtime(cracked_file_path))
                        download_interval = int(self.options.get('download_interval', 3600))
                        if last_check is not None and ((datetime.now() - last_check).seconds / download_interval) < 1:
                            return

                    self._download_from_wpasec(cracked_file_path)
                    if 'single_files' in self.options and self.options['single_files']:
                        self._write_cracked_single_files(cracked_file_path, handshake_dir)
            except Exception:
                logging.exception("WPA_SEC: Exception downloading results.")

    def _upload_to_wpasec(self, path, timeout=30):
        """
        Uploads the file to wpasec
        """
        with open(path, 'rb') as file_to_upload:
            cookie = {'key': self.options['api_key']}
            payload = {'file': file_to_upload}

            result = requests.post(
                self.options['api_url'],
                cookies=cookie,
                files=payload,
                timeout=timeout
            )
            result.raise_for_status()
            
            response = result.text.partition('\n')[0]
            
            logging.debug("WPA_SEC: Response uploading %s: %s.", path, response)
            
            return response

    def _download_from_wpasec(self, output, timeout=30):
        """
        Downloads the results from wpasec and saves them to output

        Output-Format: bssid, station_mac, ssid, password
        """
        api_url = self.options['api_url']
        if not api_url.endswith('/'):
            api_url = f"{api_url}/"
        api_url = f"{api_url}?api&dl=1"

        cookie = {'key': self.options['api_key']}

        logging.info("WPA_SEC: Downloading cracked passwords...")

        result = requests.get(api_url, cookies=cookie, timeout=timeout)
        result.raise_for_status()

        with open(output, 'wb') as output_file:
            output_file.write(result.content)

        logging.info("WPA_SEC: Downloaded cracked passwords.")

    def _write_cracked_single_files(self, cracked_file_path, handshake_dir):
        """
        Splits download results from wpasec into individual .pcap..cracked files in handshake_dir

        Each .pcap.cracked file will contain the cracked handshake password
        """
        logging.info("WPA_SEC: Writing cracked single files...")

        with open(cracked_file_path, 'r') as cracked_file:
            for line in cracked_file:
                try:
                    bssid,station_mac,ssid,password = line.split(":")
                    if password:
                        handshake_filename = re.sub(r'[^a-zA-Z0-9]', '', ssid) + '_' + bssid
                        pcap_path = os.path.join(handshake_dir, handshake_filename+'.pcap')
                        pcap_cracked_path = os.path.join(handshake_dir, handshake_filename+'.pcap.cracked')
                        if os.path.exists(pcap_path) and not os.path.exists(pcap_cracked_path):
                            with open(pcap_cracked_path, 'w') as f:
                                f.write(password)
                except Exception:
                    logging.exception(f"WPA_SEC: Exception writing cracked single file, parsing line {line}.")
    
        logging.info("WPA_SEC: Wrote cracked single files.")

    def on_webhook(self, path, request):
        from flask import make_response
        
        html_content = f'''
            <html>
                <body>
                    <form id="postForm" action="{self.options['api_url']}" method="POST">
                        <input type="hidden" name="key" value="{self.options['api_key']}">
                    </form>
                    <script type="text/javascript">
                        document.getElementById('postForm').submit();
                    </script>
                </body>
            </html>
        '''
        
        return make_response(html_content)