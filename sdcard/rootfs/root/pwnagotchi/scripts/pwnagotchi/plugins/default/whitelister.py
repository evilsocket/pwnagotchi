__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '1.0.0'
__name__ = 'whitelister'
__license__ = 'GPL3'
__description__ = 'This plugin adds the mac to a whitelist, after it got pwned.'
__enabled__ = False

import logging


def on_handshake(agent, filename, access_point, client_station):

    # Get session data
    info = agent.session()

    # Get macs which are already in whitelist
    old_skips = info['env']['data']['wifi.deauth.skip']

    ap_mac = access_point
    sta_mac = client_station

    if isinstance(access_point, dict):
        ap_mac = access_point['mac']

    if isinstance(client_station, dict):
        sta_mac = client_station['mac']

    try:
        agent.run(f"set wifi.deauth.skip {old_skips},{ap_mac},{sta_mac}")
    except Exception:
        logging.error("Could not add mac to whitelist.")
