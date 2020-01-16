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
            'version': pwnagotchi.__version__,
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

    def fingerprint(self):
        return self._keypair.fingerprint

    def _update_advertisement(self, s):
        self._advertisement['pwnd_run'] = len(self._handshakes)
        self._advertisement['pwnd_tot'] = utils.total_unique_handshakes(self._config['bettercap']['handshakes'])
        self._advertisement['uptime'] = pwnagotchi.uptime()
        self._advertisement['epoch'] = self._epoch.epoch
        grid.set_advertisement_data(self._advertisement)

    def start_advertising(self):
        if self._config['personality']['advertise']:
            _thread.start_new_thread(self._adv_poller, ())

            grid.set_advertisement_data(self._advertisement)
            grid.advertise(True)
            self._view.on_state_change('face', self._on_face_change)
        else:
            logging.warning("advertising is disabled")

    def _on_face_change(self, old, new):
        self._advertisement['face'] = new
        grid.set_advertisement_data(self._advertisement)

    def cumulative_encounters(self):
        return sum(peer.encounters for _, peer in self._peers.items())

    def _on_new_peer(self, peer):
        logging.info("new peer %s detected (%d encounters)" % (peer.full_name(), peer.encounters))
        self._view.on_new_peer(peer)
        plugins.on('peer_detected', self, peer)

    def _on_lost_peer(self, peer):
        logging.info("lost peer %s" % peer.full_name())
        self._view.on_lost_peer(peer)
        plugins.on('peer_lost', self, peer)

    def _adv_poller(self):
        # give the system a few seconds to start the first time so that any expressions
        # due to nearby units will be rendered properly
        time.sleep(20)
        while True:
            try:
                logging.debug("polling pwngrid-peer for peers ...")

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
                        to_delete.append(ident)

                for ident in to_delete:
                    self._on_lost_peer(self._peers[ident])
                    del self._peers[ident]

                for ident, peer in new_peers.items():
                    # check who's new
                    if ident not in self._peers:
                        self._peers[ident] = peer
                        self._on_new_peer(peer)
                    # update the rest
                    else:
                        self._peers[ident].update(peer)

            except Exception as e:
                logging.warning("error while polling pwngrid-peer: %s" % e)
                logging.debug(e, exc_info=True)

            time.sleep(3)
