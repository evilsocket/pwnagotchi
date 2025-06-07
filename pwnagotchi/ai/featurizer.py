import numpy as np

import pwnagotchi.mesh.wifi as wifi

MAX_EPOCH_DURATION = 1024

# RSSI normalization constants
RSSI_MIN_EXPECTED = -100.0
RSSI_MAX_EXPECTED = -20.0
# Denominator for normalization: (RSSI_MAX_EXPECTED - RSSI_MIN_EXPECTED)
RSSI_RANGE = RSSI_MAX_EXPECTED - RSSI_MIN_EXPECTED
if RSSI_RANGE == 0: # Avoid division by zero, though not with current constants
    RSSI_RANGE = 1.0


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
                            # RSSI min per channel
                            histogram_size +
                            # RSSI max per channel
                            histogram_size +
                            # RSSI avg per channel
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

    # Normalize RSSI histograms
    rssi_min_hist = np.array(state['rssi_min_histogram'])
    rssi_max_hist = np.array(state['rssi_max_histogram'])
    rssi_avg_hist = np.array(state['rssi_avg_histogram'])

    norm_rssi_min = np.clip((rssi_min_hist - RSSI_MIN_EXPECTED) / RSSI_RANGE, 0.0, 1.0)
    norm_rssi_max = np.clip((rssi_max_hist - RSSI_MIN_EXPECTED) / RSSI_RANGE, 0.0, 1.0)
    norm_rssi_avg = np.clip((rssi_avg_hist - RSSI_MIN_EXPECTED) / RSSI_RANGE, 0.0, 1.0)

    return np.concatenate((
        # aps per channel
        state['aps_histogram'],
        # clients per channel
        state['sta_histogram'],
        # peers per channel
        state['peers_histogram'],
        # RSSI features
        norm_rssi_min,
        norm_rssi_max,
        norm_rssi_avg,
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
