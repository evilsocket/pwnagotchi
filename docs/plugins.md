# Plugins

Pwnagotchi has a simple plugins system that you can use to customize your unit and its behaviour. You can place your plugins anywhere
as python files and then edit the `config.yml` file (`main.plugins` value) to point to their containing folder. Check the [plugins folder](https://github.com/evilsocket/pwnagotchi/tree/master/sdcard/rootfs/root/pwnagotchi/scripts/pwnagotchi/plugins/default/) for a list of default
plugins and all the callbacks that you can define for your own customizations.

Here's as an example the GPS plugin:

```python
__author__ = 'evilsocket@gmail.com'
__version__ = '1.0.0'
__name__ = 'gps'
__license__ = 'GPL3'
__description__ = 'Save GPS coordinates whenever an handshake is captured.'
__enabled__ = True  # set to false if you just don't use GPS

import core
import json
import os

device = '/dev/ttyUSB0'
speed = 19200
running = False


def on_loaded():
     logging.info("GPS plugin loaded for %s" % device)


def on_ready(agent):
    global running

    if os.path.exists(device):
         logging.info("enabling GPS bettercap's module for %s" % device)
        try:
            agent.run('gps off')
        except:
            pass

        agent.run('set gps.device %s' % device)
        agent.run('set gps.speed %d' % speed)
        agent.run('gps on')
        running = True
    else:
         logging.info("no GPS detected")


def on_handshake(agent, filename, access_point, client_station):
    if running:
        info = agent.session()
        gps = info['gps']
        gps_filename = filename.replace('.pcap', '.gps.json')

         logging.info("saving GPS to %s (%s)" % (gps_filename, gps))
        with open(gps_filename, 'w+t') as fp:
            json.dump(gps, fp)
```
