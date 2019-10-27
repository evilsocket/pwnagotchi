__author__ = 'diemelcw@gmail.com'
__version__ = '1.0.0'
__name__ = 'unfiltered_example'
__license__ = 'GPL3'
__description__ = 'An example plugin for pwnagotchi that implements on_unfiltered_ap_list(agent,aps)'

import logging

# Will be set with the options in config.yml config['main']['plugins'][__name__]
OPTIONS = dict()

# called when the plugin is loaded
def on_loaded():
    logging.warning("%s plugin loaded" % __name__)
    
# called when AP list is ready, before whitelist filtering has occurred
def on_unfiltered_ap_list(agent,aps):
    logging.info("Unfiltered AP list to follow")
    for ap in aps:
        logging.info(ap['hostname'])
    
    ## Additional logic here ##
