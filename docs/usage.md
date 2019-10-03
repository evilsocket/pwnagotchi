### UI

The UI is available either via display if installed, or via http://pwnagotchi.local:8080/ if you connect to the unit via `usb0` and set a static address on the network interface (change `pwnagotchi` with the hostname of your unit).

![ui](https://i.imgur.com/XgIrcur.png)

* **CH**: Current channel the unit is operating on or `*` when hopping on all channels.
* **APS**: Number of access points on the current channel and total visible access points.
* **UP**: Time since the unit has been activated.
* **PWND**: Number of handshakes captured in this session and number of unique networks we own at least one handshake of, from the beginning.
* **AUTO**: This indicates that the algorithm is running with AI disabled (or still loading), it disappears once the AI dependencies have been bootrapped and the neural network loaded.

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

