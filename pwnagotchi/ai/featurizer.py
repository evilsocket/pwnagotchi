import numpy as np

import pwnagotchi.mesh.wifi as wifi

MAX_EPOCH_DURATION = 1024


def describe(extended=False):
    if not extended:
        histogram_size = wifi.NumChannels
    else:
        # see https://github.com/evilsocket/pwnagotchi/issues/583
        histogram_size = wifi.NumChannelsExt

    return histogram_size, (1,
                            # aps per channel
                            histogram_size +
                            # clients per channel
                            histogram_size +
                            # peers per channel
                            histogram_size +
                            # duration
                            1 +
                            # inactive
                            1 +
                            # active
                            1 +
                            # missed
                            1 +
                            # hops
                            1 +
                            # deauths
                            1 +
                            # assocs
                            1 +
                            # handshakes
                            1)


def featurize(state, step):
    tot_epochs = step + 1e-10
    tot_interactions = (state['num_deauths'] + state['num_associations']) + 1e-10
    return np.concatenate((
        # aps per channel
        state['aps_histogram'],
        # clients per channel
        state['sta_histogram'],
        # peers per channel
        state['peers_histogram'],
        # duration
        [np.clip(state['duration_secs'] / MAX_EPOCH_DURATION, 0.0, 1.0)],
        # inactive
        [state['inactive_for_epochs'] / tot_epochs],
        # active
        [state['active_for_epochs'] / tot_epochs],
        # missed
        [state['missed_interactions'] / tot_interactions],
        # hops
        [state['num_hops'] / wifi.NumChannels],
        # deauths
        [state['num_deauths'] / tot_interactions],
        # assocs
        [state['num_associations'] / tot_interactions],
        # handshakes
        [state['num_handshakes'] / tot_interactions],
    ))
