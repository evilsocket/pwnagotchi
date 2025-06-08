import time
import json
import os
import re
import logging
import asyncio
import _thread
import random

import pwnagotchi
import pwnagotchi.utils as utils
import pwnagotchi.plugins as plugins
from pwnagotchi.ui.web.server import Server
from pwnagotchi.automata import Automata
from pwnagotchi.log import LastSession
from pwnagotchi.bettercap import Client
from pwnagotchi.mesh.utils import AsyncAdvertiser
from pwnagotchi.ai.train import AsyncTrainer

RECOVERY_DATA_FILE = '/root/.pwnagotchi-recovery'


class Agent(Client, Automata, AsyncAdvertiser, AsyncTrainer):
    def __init__(self, view, config, keypair):
        Client.__init__(self, config['bettercap']['hostname'],
                        config['bettercap']['scheme'],
                        config['bettercap']['port'],
                        config['bettercap']['username'],
                        config['bettercap']['password'])
        Automata.__init__(self, config, view)
        AsyncAdvertiser.__init__(self, config, view, keypair)
        AsyncTrainer.__init__(self, config)

        self._started_at = time.time()
        self._filter = None if not config['main']['filter'] else re.compile(config['main']['filter'])
        self._current_channel = 0
        self._tot_aps = 0
        self._aps_on_channel = 0
        self._supported_channels = utils.iface_channels(config['main']['iface'])
        self._view = view
        self._view.set_agent(self)
        self._web_ui = Server(self, config['ui'])

        self._access_points = []
        self._last_pwnd = None
        self._history = {}
        self._handshakes = {}
        self.last_session = LastSession(self._config)
        self.mode = 'auto'
        self.current_attack_mode = 0  # 0: Passive, 1: Broadcast Deauth, 2: Targeted Deauth
        self.ai_channel_weights = {} # For AI-controlled channel priorities
        self.current_target_ap_index = -1 # For AI-selected target AP (-1 or None if no target)

        if not os.path.exists(config['bettercap']['handshakes']):
            os.makedirs(config['bettercap']['handshakes'])

        logging.info("%s@%s (v%s)", pwnagotchi.name(), self.fingerprint(), pwnagotchi.__version__)
        for _, plugin in plugins.loaded.items():
            logging.debug("plugin '%s' v%s", plugin.__class__.__name__, plugin.__version__)

    def config(self):
        return self._config

    def view(self):
        return self._view

    def supported_channels(self):
        return self._supported_channels

    def setup_events(self):
        logging.info("connecting to %s ...", self.url)

        for tag in self._config['bettercap']['silence']:
            try:
                self.run('events.ignore %s' % tag, verbose_errors=False)
            except Exception:
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
                    logging.info("found monitor interface: %s", iface['name'])
                    has_mon = True
                    break

            if has_mon is False:
                if mon_start_cmd is not None and mon_start_cmd != '':
                    logging.info("starting monitor interface ...")
                    self.run('!%s' % mon_start_cmd)
                else:
                    logging.info("waiting for monitor interface %s ...", mon_iface)
                    time.sleep(1)

        logging.info("supported channels: %s", self._supported_channels)
        logging.info("handshakes will be collected inside %s", self._config['bettercap']['handshakes'])

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

    def _wait_bettercap(self):
        while True:
            try:
                _s = self.session()
                return
            except Exception:
                logging.info("waiting for bettercap API to be available ...")
                time.sleep(1)

    def start(self):
        self.start_ai()
        self._wait_bettercap()
        self.setup_events()
        self.set_starting()
        self.start_monitor_mode()
        self.start_event_polling()
        self.start_session_fetcher()
        # print initial stats
        self.next_epoch()
        self.set_ready()

    def on_ai_policy(self, policy):
        # This method is called when the AI decides on a new policy (set of parameters)
        # It needs to handle the 'attack_mode' and other parameters AI might control.

        new_attack_mode = policy.get('attack_mode', 0) # Default to passive (0)
        if new_attack_mode != self.current_attack_mode:
            logging.info(f"[ai] AI changed attack_mode from {self.current_attack_mode} to {new_attack_mode}")
            self.current_attack_mode = new_attack_mode

        new_channel_weights = policy.get('channel_weights')
        if new_channel_weights is not None and new_channel_weights != self.ai_channel_weights:
            logging.info(f"[ai] AI updated channel_weights from {self.ai_channel_weights} to {new_channel_weights}")
            self.ai_channel_weights = new_channel_weights

        new_target_ap_index = policy.get('target_ap_index', -1) # Default to -1 (invalid index)
        if new_target_ap_index != self.current_target_ap_index:
            logging.info(f"[ai] AI changed target_ap_index from {self.current_target_ap_index} to {new_target_ap_index}")
            self.current_target_ap_index = new_target_ap_index

        # Simplified handling for other parameters from AI policy
        # A full implementation would merge this with AsyncTrainer's on_ai_policy if Agent inherits it directly for this
        personality = self._config['personality']
        for param_name, value in policy.items():
            if param_name in ('attack_mode', 'channel_weights', 'target_ap_index'):  # Already handled above
                continue

            if param_name in personality:
                if personality[param_name] != value:
                    logging.info('[ai] Personality %s set by AI to %s (was %s)', param_name, value, personality[param_name])
                    personality[param_name] = value
            # Extend to other config sections if necessary, carefully
            # For example, main config:
            # elif param_name in self._config['main']:
            #    if self._config['main'][param_name] != value:
            #        logging.info('[ai] Main config %s set by AI to %s (was %s)', param_name, value, self._config['main'][param_name])
            #        self._config['main'][param_name] = value
            else:
                # Only log if it's not a known config to avoid noise, or handle specifically if AI can set new params
                if param_name not in personality and param_name not in self._config['main'] and param_name not in self._config['ui']['display']:
                     logging.warning(f"[ai] AI tried to set unknown parameter: {param_name} to {value}")


    def _handle_ai_deauth_actions(self):
        if not self._config['personality']['deauth']: # Respect global deauth toggle
            logging.debug("[ai] Deauth actions skipped (deauth personality globally disabled).")
            return

        if self.current_attack_mode == 1: # Mode 1 is Broadcast Deauth
            logging.info("[ai] Attack Mode 1: Triggering broadcast deauthentication.")
            try:
                self.run('wifi.deauth *')
                self._epoch.track(deauth=True, inc=1)
            except Exception as e:
                logging.error(f"[ai] Error during broadcast deauth: {e}")

        elif self.current_attack_mode == 2: # Mode 2 is AI-Selected Targeted Deauth
            if self.current_target_ap_index is not None and self.current_target_ap_index >= 0:
                epoch_data = self._epoch.data() # Call once
                featured_bssids = epoch_data.get('_featured_ap_bssids', [])

                if 0 <= self.current_target_ap_index < len(featured_bssids):
                    target_bssid = featured_bssids[self.current_target_ap_index]
                    if target_bssid: # Check if BSSID is not None or empty
                        logging.info(f"[ai] Attack Mode 2: Performing AI-selected targeted deauth on BSSID {target_bssid} (index {self.current_target_ap_index}).")
                        try:
                            self.run(f'wifi.deauth {target_bssid}')
                            self._epoch.track(deauth=True, inc=1)
                        except Exception as e:
                            logging.error(f"[ai] Error during AI-selected targeted deauth on {target_bssid}: {e}")
                    else:
                        logging.debug(f"[ai] Attack Mode 2: AI selected target_ap_index {self.current_target_ap_index}, but BSSID is None (padding). No deauth.")
                else:
                    logging.warning(f"[ai] Attack Mode 2: AI selected target_ap_index {self.current_target_ap_index} is out of bounds for featured_bssids list (len {len(featured_bssids)}). No deauth.")
            else:
                logging.debug(f"[ai] Attack Mode 2: No valid target_ap_index ({self.current_target_ap_index}). No AI-selected targeted deauth.")

        elif self.current_attack_mode == 0: # Passive
            logging.debug("[ai] Attack Mode 0 (Passive): No deauth actions taken by _handle_ai_deauth_actions.")
            # No active deauth actions in passive mode

    def recon(self):
        # Call AI deauth handler based on AI mode
        self._handle_ai_deauth_actions()

        recon_time = self._config['personality']['recon_time']
        max_inactive = self._config['personality']['max_inactive_scale']
        recon_mul = self._config['personality']['recon_inactive_multiplier']
        channels = self._config['personality']['channels']

        if self._epoch.inactive_for >= max_inactive:
            recon_time *= recon_mul

        self._view.set('channel', '*')

        if not channels:
            self._current_channel = 0
            logging.debug("RECON %ds", recon_time)
            self.run('wifi.recon.channel clear')
        else:
            logging.debug("RECON %ds ON CHANNELS %s", recon_time, ','.join(map(str, channels)))
            try:
                self.run('wifi.recon.channel %s' % ','.join(map(str, channels)))
            except Exception as e:
                logging.exception("Error while setting wifi.recon.channels (%s)", e)

        self.wait_for(recon_time, sleeping=False)

    def _filter_included(self, ap):
        return self._filter is None or \
               self._filter.match(ap['hostname']) is not None or \
               self._filter.match(ap['mac']) is not None

    def set_access_points(self, aps):
        self._access_points = aps
        plugins.on('wifi_update', self, aps)
        self._epoch.observe(aps, list(self._peers.values()))
        return self._access_points

    def get_access_points(self):
        whitelist = self._config['main']['whitelist']
        aps = []
        try:
            s = self.session()
            plugins.on("unfiltered_ap_list", self, s['wifi']['aps'])
            for ap in s['wifi']['aps']:
                if ap['encryption'] == '' or ap['encryption'] == 'OPEN':
                    continue
                elif ap['hostname'] not in whitelist \
                        and ap['mac'].lower() not in whitelist \
                        and ap['mac'][:8].lower() not in whitelist:
                    if self._filter_included(ap):
                        aps.append(ap)
        except Exception as e:
            logging.exception("Error while getting acces points (%s)", e)

        aps.sort(key=lambda ap: ap['channel'])
        return self.set_access_points(aps)

    def get_total_aps(self):
        return self._tot_aps

    def get_aps_on_channel(self):
        return self._aps_on_channel

    def get_current_channel(self):
        return self._current_channel

    def get_access_points_by_channel(self):
        aps = self.get_access_points()
        channels = self._config['personality']['channels']
        grouped = {}

        # group by channel
        for ap in aps:
            ch = ap['channel']
            # if we're sticking to a channel, skip anything
            # which is not on that channel
            if channels and ch not in channels:
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
        secs = pwnagotchi.uptime()
        self._view.set('uptime', utils.secs_to_hhmmss(secs))
        # self._view.set('epoch', '%04d' % self._epoch.epoch)

    def _update_counters(self):
        self._tot_aps = len(self._access_points)
        tot_stas = sum(len(ap['clients']) for ap in self._access_points)
        if self._current_channel == 0:
            self._view.set('aps', '%d' % self._tot_aps)
            self._view.set('sta', '%d' % tot_stas)
        else:
            self._aps_on_channel = len([ap for ap in self._access_points if ap['channel'] == self._current_channel])
            stas_on_channel = sum(
                [len(ap['clients']) for ap in self._access_points if ap['channel'] == self._current_channel])
            self._view.set('aps', '%d (%d)' % (self._aps_on_channel, self._tot_aps))
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

    def _update_peers(self):
        self._view.set_closest_peer(self._closest_peer, len(self._peers))

    def _reboot(self):
        self.set_rebooting()
        self._save_recovery_data()
        pwnagotchi.reboot()

    def _save_recovery_data(self):
        logging.warning("writing recovery data to %s ...", RECOVERY_DATA_FILE)
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
                logging.info("found recovery data: %s", data)
                self._started_at = data['started_at']
                self._epoch.epoch = data['epoch']
                self._handshakes = data['handshakes']
                self._history = data['history']
                self._last_pwnd = data['last_pwnd']

                if delete:
                    logging.info("deleting %s", RECOVERY_DATA_FILE)
                    os.unlink(RECOVERY_DATA_FILE)
        except:
            if not no_exceptions:
                raise


    def start_session_fetcher(self):
        _thread.start_new_thread(self._fetch_stats, ())


    def _fetch_stats(self):
        while True:
            s = self.session()
            self._update_uptime(s)
            self._update_advertisement(s)
            self._update_peers()
            self._update_counters()
            self._update_handshakes(0)
            time.sleep(1)

    async def _on_event(self, msg):
        found_handshake = False
        jmsg = json.loads(msg)

        if jmsg['tag'] == 'wifi.client.handshake':
            filename = jmsg['data']['file']
            sta_mac = jmsg['data']['station']
            ap_mac = jmsg['data']['ap']
            key = "%s -> %s" % (sta_mac, ap_mac)
            if key not in self._handshakes:
                self._handshakes[key] = jmsg
                s = self.session()
                ap_and_station = self._find_ap_sta_in(sta_mac, ap_mac, s)
                if ap_and_station is None:
                    logging.warning("!!! captured new handshake: %s !!!", key)
                    self._last_pwnd = ap_mac
                    plugins.on('handshake', self, filename, ap_mac, sta_mac)
                else:
                    (ap, sta) = ap_and_station
                    self._last_pwnd = ap['hostname'] if ap['hostname'] != '' and ap[
                        'hostname'] != '<hidden>' else ap_mac
                    logging.warning(
                        "!!! captured new handshake on channel %d, %d dBm: %s (%s) -> %s [%s (%s)] !!!",
                            ap['channel'],
                            ap['rssi'],
                            sta['mac'], sta['vendor'],
                            ap['hostname'], ap['mac'], ap['vendor'])
                    plugins.on('handshake', self, filename, ap, sta)
                found_handshake = True
            self._update_handshakes(1 if found_handshake else 0)

    def _event_poller(self, loop):
        self._load_recovery_data()
        self.run('events.clear')

        while True:
            logging.debug("polling events ...")
            try:
                loop.create_task(self.start_websocket(self._on_event))
                loop.run_forever()
            except Exception as ex:
                logging.debug("Error while polling via websocket (%s)", ex)

    def start_event_polling(self):
        # start a thread and pass in the mainloop
        _thread.start_new_thread(self._event_poller, (asyncio.get_event_loop(),))


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

    def associate(self, ap, throttle=0):
        if self.is_stale():
            logging.debug("recon is stale, skipping assoc(%s)", ap['mac'])
            return

        if self._config['personality']['associate'] and self._should_interact(ap['mac']):
            self._view.on_assoc(ap)

            try:
                logging.info("sending association frame to %s (%s %s) on channel %d [%d clients], %d dBm...",
                    ap['hostname'], ap['mac'], ap['vendor'], ap['channel'], len(ap['clients']), ap['rssi'])
                self.run('wifi.assoc %s' % ap['mac'])
                self._epoch.track(assoc=True)
            except Exception as e:
                self._on_error(ap['mac'], e)

            plugins.on('association', self, ap)
            if throttle > 0:
                time.sleep(throttle)
            self._view.on_normal()

    def deauth(self, ap, sta, throttle=0):
        # AI Attack Mode Check for Targeted Deauth (Mode 2)
        if self.current_attack_mode == 0: # Passive
            logging.info(f"[ai] Attack Mode 0 (Passive): Targeted deauth for {sta['mac']} on AP {ap['mac']} skipped.")
            return
        if self.current_attack_mode == 1: # Broadcast mode
            logging.info(f"[ai] Attack Mode 1 (Broadcast): Targeted deauth for {sta['mac']} on AP {ap['mac']} skipped in favor of broadcast.")
            return

        # If mode is 2 (Targeted), it proceeds with the original logic.
        # If mode is not explicitly 0 or 1, it also proceeds (default/fallback behavior).
        if self.current_attack_mode == 2:
            logging.info(f"[ai] Attack Mode 2 (Targeted): Proceeding with targeted deauth for {sta['mac']} on AP {ap['mac']}.")

        if self.is_stale():
            logging.debug("recon is stale, skipping deauth(%s)", sta['mac'])
            return

        if self._config['personality']['deauth'] and self._should_interact(sta['mac']):
            self._view.on_deauth(sta)

            try:
                logging.info("deauthing %s (%s) from %s (%s %s) on channel %d, %d dBm ...",
                    sta['mac'], sta['vendor'], ap['hostname'], ap['mac'], ap['vendor'], ap['channel'], ap['rssi'])
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
            logging.debug("recon is stale, skipping set_channel(%d)", channel)
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
                    logging.info("waiting for %ds on channel %d ...", wait, self._current_channel)
                else:
                    logging.debug("waiting for %ds on channel %d ...", wait, self._current_channel)
                self.wait_for(wait)
            if verbose and self._epoch.any_activity:
                logging.info("CHANNEL %d", channel)
            try:
                self.run('wifi.recon.channel %d' % channel)
                self._current_channel = channel
                self._epoch.track(hop=True)
                self._view.set('channel', '%d' % channel)

                plugins.on('channel_hop', self, channel)

            except Exception as e:
                logging.error("Error while setting channel (%s)", e)

    def _next_recon_channel(self):
        # AI Weighted Channel Selection
        if self.ai_channel_weights:
            supported_chan_list = self.supported_channels()  # Get this once

            weighted_channels = []
            raw_weights = []
            for ch_str, weight in self.ai_channel_weights.items():
                try:
                    int_channel = int(ch_str) # AI model might output channel as string key
                    if float(weight) > 0 and int_channel in supported_chan_list:
                        weighted_channels.append(int_channel)
                        raw_weights.append(float(weight))
                except ValueError:
                    logging.warning(f"[ai] Could not parse channel '{ch_str}' or weight '{weight}' from ai_channel_weights.")
                    continue

            if weighted_channels:  # If there are any valid channels with positive weights
                # Exploration Factor: 10% chance to pick a random supported channel
                if random.random() < 0.10:
                    selected_channel = random.choice(supported_chan_list)
                    logging.info(f"[ai] Channel Hopping: Exploring randomly to channel {selected_channel} (from {len(supported_chan_list)} supported).")
                    return selected_channel
                else:
                    total_weight = sum(raw_weights)
                    if total_weight > 0:
                        probabilities = [w / total_weight for w in raw_weights]
                        selected_channel = random.choices(weighted_channels, weights=probabilities, k=1)[0]
                        logging.info(f"[ai] Channel Hopping: Selected channel {selected_channel} using AI weights.")
                        # More detailed log for debugging, perhaps less frequent or under a specific debug flag if too verbose
                        logging.debug(f"[ai] Full AI weights: {self.ai_channel_weights}, Filtered (chan,prob): {list(zip(weighted_channels, probabilities))}")
                        return selected_channel
                    else:
                        # This case should ideally not be reached if weighted_channels is not empty and weights are > 0
                        logging.debug("[ai] Channel Hopping: All AI-weighted channels had zero effective weight after filtering. Falling back to default logic.")
            else:
                logging.debug("[ai] Channel Hopping: No valid (supported, positive weight) AI channel weights found. Falling back to default logic.")
        else:
            logging.debug("[ai] Channel Hopping: AI channel weights are empty. Using default logic.")

        # Fallback to original Automata._next_recon_channel logic
        # super(Agent, self)._next_recon_channel() # Would be ideal if inheritance setup allows easy super() call to specific parent method
        # Replicating Automata's logic here:
        channels = self._config['personality']['channels']
        if not channels:
            # hop randomly if no channels are specified
            # Ensure supported_channels() is available and returns a list
            supported = self.supported_channels()
            if not supported:
                logging.error("[ai] No supported channels found for random hopping! Defaulting to channel 1.")
                return 1 # Should not happen in a normal setup
            selected_channel = random.choice(supported)
            logging.debug(f"[ai] Channel Hopping (Default): No personality channels, randomly selected {selected_channel}.")
            return selected_channel

        # Cycle through personality channels
        # self._recon_idx is part of Automata state
        self._recon_idx = (self._recon_idx + 1) % len(channels)
        selected_channel = channels[self._recon_idx]
        logging.debug(f"[ai] Channel Hopping (Default): Cycling personality channels, selected {selected_channel}.")
        return selected_channel
