### User Interface

The UI is available either via display if installed, or via http://pwnagotchi.local:8080/ if you connect to the unit via `usb0` and set a static address on the network interface (change `pwnagotchi` with the hostname of your unit).

![ui](https://i.imgur.com/XgIrcur.png)

* **CH**: Current channel the unit is operating on or `*` when hopping on all channels.
* **APS**: Number of access points on the current channel and total visible access points.
* **UP**: Time since the unit has been activated.
* **PWND**: Number of handshakes captured in this session and number of unique networks we own at least one handshake of, from the beginning.
* **AUTO**: This indicates that the algorithm is running with AI disabled (or still loading), it disappears once the AI dependencies have been bootrapped and the neural network loaded.

### Training the AI

At its core Pwnagotchi is a very simple creature: we could summarize its main algorithm as:

```python
# main loop
while True:
    # ask bettercap for all visible access points and their clients
    aps = get_all_visible_access_points()
    # loop each AP
    for ap in aps:
        # send an association frame in order to grab the PMKID
        send_assoc(ap)
        # loop each client station of the AP
        for client in ap.clients:
            # deauthenticate the client to get its half or full handshake
            deauthenticate(client)
    
    wait_for_loot()
```

Despite its simplicity, this logic is controlled by several parameters that regulate the wait times, the timeouts, on which channels to hop and so on.

From `config.yml`:

```yaml
personality:
    # advertise our presence
    advertise: true
    # perform a deauthentication attack to client stations in order to get full or half handshakes
    deauth: true
    # send association frames to APs in order to get the PMKID
    associate: true
    # list of channels to recon on, or empty for all channels
    channels: []
    # minimum WiFi signal strength in dBm
    min_rssi: -200
    # number of seconds for wifi.ap.ttl
    ap_ttl: 120
    # number of seconds for wifi.sta.ttl
    sta_ttl: 300
    # time in seconds to wait during channel recon
    recon_time: 30
    # number of inactive epochs after which recon_time gets multiplied by recon_inactive_multiplier
    max_inactive_scale: 2
    # if more than max_inactive_scale epochs are inactive, recon_time *= recon_inactive_multiplier
    recon_inactive_multiplier: 2
    # time in seconds to wait during channel hopping if activity has been performed
    hop_recon_time: 10
    # time in seconds to wait during channel hopping if no activity has been performed
    min_recon_time: 5
    # maximum amount of deauths/associations per BSSID per session
    max_interactions: 3
    # maximum amount of misses before considering the data stale and triggering a new recon
    max_misses_for_recon: 5
    # number of active epochs that triggers the excited state
    excited_num_epochs: 10
    # number of inactive epochs that triggers the bored state
    bored_num_epochs: 15
    # number of inactive epochs that triggers the sad state
    sad_num_epochs: 25
```

There is no optimal set of parameters for every situation: when the unit is moving (during a walk for instance) smaller timeouts and RSSI thresholds might be preferred
in order to quickly remove routers that are not in range anymore, while when stationary in high density areas (like an office) other parameters might be better. 
The role of the AI is to observe what's going on at the WiFi level, and adjust those parameters in order to maximize the cumulative reward of that loop / epoch.

#### Reward Function

After each iteration of the main loop (an `epoch`), the reward, a score that represents how well the parameters performed, is computed as 
(an excerpt from `pwnagotchi/ai/reward.py`):

```python
# state contains the information of the last epoch
# epoch_n is the number of the last epoch
tot_epochs = epoch_n + 1e-20 # 1e-20 is added to avoid a division by 0
tot_interactions = max(state['num_deauths'] + state['num_associations'], state['num_handshakes']) + 1e-20
tot_channels = wifi.NumChannels

# ideally, for each interaction we would have an handshake
h = state['num_handshakes'] / tot_interactions
# small positive rewards the more active epochs we have
a = .2 * (state['active_for_epochs'] / tot_epochs)
# make sure we keep hopping on the widest channel spectrum
c = .1 * (state['num_hops'] / tot_channels)
# small negative reward if we don't see aps for a while
b = -.3 * (state['blind_for_epochs'] / tot_epochs)
# small negative reward if we interact with things that are not in range anymore
m = -.3 * (state['missed_interactions'] / tot_interactions)
# small negative reward for inactive epochs
i = -.2 * (state['inactive_for_epochs'] / tot_epochs)

reward = h + a + c + b + i + m
```

By maximizing this reward value, the AI learns over time to find the set of parameters that better perform with the current environmental conditions.


### BetterCAP's Web UI

Moreover, given that the unit is running bettercap with API and Web UI, you'll be able to use the unit as a WiFi penetration testing portable station
by accessing `http://pwnagotchi.local/`.

![webui](https://raw.githubusercontent.com/bettercap/media/master/ui-events.png)

### Update your Pwnagotchi

You can use the `scripts/update_pwnagotchi.sh` script to update to the most recent version of pwnagotchi.

```shell
usage: ./update_pwnagitchi.sh [OPTIONS]

   Options:
      -v                # Version to update to, can be a branch or commit. (default: master)
      -u                # Url to clone from. (default: https://github.com/evilsocket/pwnagotchi)
      -m                # Mode to restart to. (Supported: auto manual; default: auto)
      -b                # Backup the current pwnagotchi config.
      -r                # Restore the current pwnagotchi config. -b will be enabled.
      -h                # Shows this help.             Shows this help.

```

### Backup your Pwnagotchi

You can use the `scripts/backup.sh` script to backup the important files of your unit.

```shell
usage: ./scripts/backup.sh HOSTNAME backup.zip
```

### Random Info

- **On a rpi0w, it'll take approximately 30 minutes to load the AI**.
- `/var/log/pwnagotchi.log` is your friend.
- if connected to a laptop via usb data port, with internet connectivity shared, magic things will happen.
- checkout the `ui.video` section of the `config.yml` - if you don't want to use a display, you can connect to it with the browser and a cable.
- If you get `[FAILED] Failed to start Remount Root and Kernel File Systems.` while booting pwnagotchi, make sure
the `PARTUUID`s for `rootfs` and `boot` partitions are the same in `/etc/fstab`. Use `sudo blkid` to find those values when you are using `create_sibling.sh`.

