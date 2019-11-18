from threading import Event
import _thread
import logging
import time

import pwnagotchi.plugins as plugins


class Led(plugins.Plugin):
    __author__ = 'evilsocket@gmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'This plugin blinks the PWR led with different patterns depending on the event.'

    def __init__(self):
        self._is_busy = False
        self._event = Event()
        self._event_name = None
        self._led_file = "/sys/class/leds/led0/brightness"
        self._delay = 200

    # called when the plugin is loaded
    def on_loaded(self):
        self._led_file = "/sys/class/leds/led%d/brightness" % self.options['led']
        self._delay = int(self.options['delay'])

        logging.info("[led] plugin loaded for %s" % self._led_file)
        self._on_event('loaded')
        _thread.start_new_thread(self._worker, ())

    def _on_event(self, event):
        if not self._is_busy:
            self._event_name = event
            self._event.set()
            logging.debug("[led] event '%s' set", event)
        else:
            logging.debug("[led] skipping event '%s' because the worker is busy", event)

    def _led(self, on):
        with open(self._led_file, 'wt') as fp:
            fp.write(str(on))

    def _blink(self, pattern):
        logging.debug("[led] using pattern '%s' ..." % pattern)
        for c in pattern:
            if c == ' ':
                self._led(1)
            else:
                self._led(0)
            time.sleep(self._delay / 1000.0)
        # reset
        self._led(0)

    def _worker(self):
        while True:
            self._event.wait()
            self._event.clear()
            self._is_busy = True

            try:
                if self._event_name in self.options['patterns']:
                    pattern = self.options['patterns'][self._event_name]
                    self._blink(pattern)
                else:
                    logging.debug("[led] no pattern defined for %s" % self._event_name)
            except Exception as e:
                logging.exception("[led] error while blinking")

            finally:
                self._is_busy = False

    # called when the unit is updating its software
    def on_updating(self):
        self._on_event('updating')

    # called when there's one or more unread pwnmail messages
    def on_unread_inbox(self, num_unread):
        self._on_event('unread_inbox')

    # called when there's internet connectivity
    def on_internet_available(self, agent):
        self._on_event('internet_available')

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        self._on_event('ready')

    # called when the AI finished loading
    def on_ai_ready(self, agent):
        self._on_event('ai_ready')

    # called when the AI starts training for a given number of epochs
    def on_ai_training_start(self, agent, epochs):
        self._on_event('ai_training_start')

    # called when the AI got the best reward so far
    def on_ai_best_reward(self, agent, reward):
        self._on_event('ai_best_reward')

    # called when the AI got the worst reward so far
    def on_ai_worst_reward(self, agent, reward):
        self._on_event('ai_worst_reward')

    # called when the status is set to bored
    def on_bored(self, agent):
        self._on_event('bored')

    # called when the status is set to sad
    def on_sad(self, agent):
        self._on_event('sad')

    # called when the status is set to excited
    def on_excited(self, agent):
        self._on_event('excited')

    # called when the status is set to lonely
    def on_lonely(self, agent):
        self._on_event('lonely')

    # called when the agent is rebooting the board
    def on_rebooting(self, agent):
        self._on_event('rebooting')

    # called when the agent is waiting for t seconds
    def on_wait(self, agent, t):
        self._on_event('wait')

    # called when the agent is sleeping for t seconds
    def on_sleep(self, agent, t):
        self._on_event('sleep')

    # called when the agent refreshed its access points list
    def on_wifi_update(self, agent, access_points):
        self._on_event('wifi_update')

    # called when the agent is sending an association frame
    def on_association(self, agent, access_point):
        self._on_event('association')

    # called when the agent is deauthenticating a client station from an AP
    def on_deauthentication(self, agent, access_point, client_station):
        self._on_event('deauthentication')

    # called when a new handshake is captured, access_point and client_station are json objects
    # if the agent could match the BSSIDs to the current list, otherwise they are just the strings of the BSSIDs
    def on_handshake(self, agent, filename, access_point, client_station):
        self._on_event('handshake')

    # called when an epoch is over (where an epoch is a single loop of the main algorithm)
    def on_epoch(self, agent, epoch, epoch_data):
        self._on_event('epoch')

    # called when a new peer is detected
    def on_peer_detected(self, agent, peer):
        self._on_event('peer_detected')

    # called when a known peer is lost
    def on_peer_lost(self, agent, peer):
        self._on_event('peer_lost')
