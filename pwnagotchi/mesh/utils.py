import _thread
import logging
import time

import pwnagotchi
import pwnagotchi.utils as utils
import pwnagotchi.ui.faces as faces
import pwnagotchi.plugins as plugins
import pwnagotchi.grid as grid
from pwnagotchi.mesh.peer import Peer


class AsyncAdvertiser(object):
    def __init__(self, config, view, keypair):
        self._config = config
        self._view = view
        self._keypair = keypair
        self._advertisement = {
            'name': pwnagotchi.name(),
            'version': pwnagotchi.version,
            'identity': self._keypair.fingerprint,
            'face': faces.FRIEND,
            'pwnd_run': 0,
            'pwnd_tot': 0,
            'uptime': 0,
            'epoch': 0,
            'policy': self._config['personality']
        }
        self._peers = {}
        self._closest_peer = None

        _thread.start_new_thread(self._adv_poller, ())

    def _update_advertisement(self, s):
        self._advertisement['pwnd_run'] = len(self._handshakes)
        self._advertisement['pwnd_tot'] = utils.total_unique_handshakes(self._config['bettercap']['handshakes'])
        self._advertisement['uptime'] = pwnagotchi.uptime()
        self._advertisement['epoch'] = self._epoch.epoch
        grid.set_advertisement_data(self._advertisement)

    def start_advertising(self):
        if self._config['personality']['advertise']:
            grid.set_advertisement_data(self._advertisement)
            grid.advertise(True)
            self._view.on_state_change('face', self._on_face_change)
        else:
            logging.warning("advertising is disabled")

    def _on_face_change(self, old, new):
        self._advertisement['face'] = new
        grid.set_advertisement_data(self._advertisement)

    def _adv_poller(self):
        while True:
            logging.debug("polling pwngrid-peer for peers ...")

            try:
                grid_peers = grid.peers()
                new_peers = {}

                self._closest_peer = None
                for obj in grid_peers:
                    peer = Peer(obj)
                    new_peers[peer.identity()] = peer
                    if self._closest_peer is None:
                        self._closest_peer = peer

                # check who's gone
                to_delete = []
                for ident, peer in self._peers.items():
                    if ident not in new_peers:
                        self._view.on_lost_peer(peer)
                        plugins.on('peer_lost', self, peer)
                        to_delete.append(ident)

                for ident in to_delete:
                    del self._peers[ident]

                for ident, peer in new_peers:
                    # check who's new
                    if ident not in self._peers:
                        self._peers[ident] = peer
                        self._view.on_new_peer(peer)
                        plugins.on('peer_detected', self, peer)
                    # update the rest
                    else:
                        self._peers[ident].update(peer)

            except Exception as e:
                logging.exception("error while polling pwngrid-peer")

            time.sleep(1)
