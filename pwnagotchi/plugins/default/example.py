__author__ = 'evilsocket@gmail.com'
__version__ = '1.0.0'
__name__ = 'hello_world'
__license__ = 'GPL3'
__description__ = 'An example plugin for pwnagotchi that implements all the available callbacks.'

import logging

from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts


# Will be set with the options in config.yml config['main']['plugins'][__name__]
OPTIONS = dict()

# called when the plugin is loaded
def on_loaded():
    logging.warning("WARNING: plugin %s should be disabled!" % __name__)


# called in manual mode when there's internet connectivity
def on_internet_available(ui, keypair, config, log):
    pass


# called to setup the ui elements
def on_ui_setup(ui):
    # add custom UI elements
    ui.add_element('ups', LabeledValue(color=BLACK, label='UPS', value='0%/0V', position=(ui.width() / 2 - 25, 0),
                                       label_font=fonts.Bold, text_font=fonts.Medium))


# called when the ui is updated
def on_ui_update(ui):
    # update those elements
    some_voltage = 0.1
    some_capacity = 100.0

    ui.set('ups', "%4.2fV/%2i%%" % (some_voltage, some_capacity))


# called when the hardware display setup is done, display is an hardware specific object
def on_display_setup(display):
    pass


# called when everything is ready and the main loop is about to start
def on_ready(agent):
    logging.info("unit is ready")
    # you can run custom bettercap commands if you want
    #   agent.run('ble.recon on')
    # or set a custom state
    #   agent.set_bored()


# called when the AI finished loading
def on_ai_ready(agent):
    pass


# called when the AI finds a new set of parameters
def on_ai_policy(agent, policy):
    pass


# called when the AI starts training for a given number of epochs
def on_ai_training_start(agent, epochs):
    pass


# called after the AI completed a training epoch
def on_ai_training_step(agent, _locals, _globals):
    pass


# called when the AI has done training
def on_ai_training_end(agent):
    pass


# called when the AI got the best reward so far
def on_ai_best_reward(agent, reward):
    pass


# called when the AI got the worst reward so far
def on_ai_worst_reward(agent, reward):
    pass


# called when a non overlapping wifi channel is found to be free
def on_free_channel(agent, channel):
    pass


# called when the status is set to bored
def on_bored(agent):
    pass


# called when the status is set to sad
def on_sad(agent):
    pass


# called when the status is set to excited
def on_excited(agent):
    pass


# called when the status is set to lonely
def on_lonely(agent):
    pass


# called when the agent is rebooting the board
def on_rebooting(agent):
    pass


# called when the agent is waiting for t seconds
def on_wait(agent, t):
    pass


# called when the agent is sleeping for t seconds
def on_sleep(agent, t):
    pass


# called when the agent refreshed its access points list
def on_wifi_update(agent, access_points):
    pass


# called when the agent is sending an association frame
def on_association(agent, access_point):
    pass


# callend when the agent is deauthenticating a client station from an AP
def on_deauthentication(agent, access_point, client_station):
    pass


# callend when the agent is tuning on a specific channel
def on_channel_hop(agent, channel):
    pass


# called when a new handshake is captured, access_point and client_station are json objects
# if the agent could match the BSSIDs to the current list, otherwise they are just the strings of the BSSIDs
def on_handshake(agent, filename, access_point, client_station):
    pass


# called when an epoch is over (where an epoch is a single loop of the main algorithm)
def on_epoch(agent, epoch, epoch_data):
    pass


# called when a new peer is detected
def on_peer_detected(agent, peer):
    pass


# called when a known peer is lost
def on_peer_lost(agent, peer):
    pass
