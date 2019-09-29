# Pwnagotchi

<p align="center">
  <p align="center">
    <a href="https://github.com/evilsocket/pwnagotchi/releases/latest"><img alt="Release" src="https://img.shields.io/github/release/evilsocket/pwnagotchi.svg?style=flat-square"></a>
    <a href="https://github.com/evilsocket/pwnagotchi/blob/master/LICENSE.md"><img alt="Software License" src="https://img.shields.io/badge/license-GPL3-brightgreen.svg?style=flat-square"></a>
    <a href="https://travis-ci.org/evilsocket/pwnagotchi"><img alt="Travis" src="https://img.shields.io/travis/evilsocket/pwnagotchi/master.svg?style=flat-square"></a>
  </p>
</p>

[Pwnagotchi](https://twitter.com/pwnagotchi) is an "AI" that learns from the WiFi environment and instruments bettercap in order to maximize the WPA key material (any form of handshake that is crackable, including [PMKIDs](https://www.evilsocket.net/2019/02/13/Pwning-WiFi-networks-with-bettercap-and-the-PMKID-client-less-attack/), full and half WPA handshakes) captured.

![handshake](https://i.imgur.com/pdA4vCZ.png)

Specifically, it's using an [LSTM with MLP feature extractor](https://stable-baselines.readthedocs.io/en/master/modules/policies.html#stable_baselines.common.policies.MlpLstmPolicy) as its policy network for the [A2C agent](https://stable-baselines.readthedocs.io/en/master/modules/a2c.html), here is [a very good intro](https://hackernoon.com/intuitive-rl-intro-to-advantage-actor-critic-a2c-4ff545978752) on the subject.

Instead of playing [Super Mario or Atari games](https://becominghuman.ai/getting-mario-back-into-the-gym-setting-up-super-mario-bros-in-openais-gym-8e39a96c1e41?gi=c4b66c3d5ced), pwnagotchi will tune over time [its own parameters](https://github.com/evilsocket/pwnagotchi/blob/master/sdcard/rootfs/root/pwnagotchi/config.yml#L54), effectively learning to get better at pwning WiFi things. **Keep in mind:** unlike the usual RL simulations, pwnagotchi learns over time (where a single epoch can last from a few seconds to minutes, depending on how many access points and client stations are visible), do not expect it to perform amazingly well at the beginning, as it'll be exploring several combinations of parameters ... but listen to it when it's bored, bring it with you and have it observe new networks and capture new handshakes and you'll see :)

Multiple units can talk to each other, advertising their own presence using a parasite protocol I've built on top of the existing dot11 standard, by broadcasting custom information elements. Over time, two or more units learn to cooperate if they detect each other's presence, by dividing the available channels among them.

![peers](https://i.imgur.com/Ywr5aqx.png)

Depending on the status of the unit, several states and states transitions are configurable and represented on the display as different moods, expressions and sentences.

If instead you just want to use your own parameters and save battery and CPU cycles, you can disable the AI in `config.yml` and enjoy an automated deauther, WPA handshake sniffer and portable bettercap + webui dedicated hardware.

**NOTE:** The software **requires at least bettercap v2.25**.

![units](https://i.imgur.com/MStjXZF.png)

## Why

For hackers to learn reinforcement learning, WiFi networking and have an excuse to take a walk more often. And **it's cute as f---**.

## Documentation

**THIS IS STILL ALPHA STAGE SOFTWARE, IF YOU DECIDE TO TRY TO USE IT, YOU ARE ON YOUR OWN, NO SUPPORT WILL BE PROVIDED, NEITHER FOR INSTALLATION OR FOR BUGS**

However, there's [a Slack channel](https://join.slack.com/t/pwnagotchi/shared_invite/enQtNzc4NzY3MDE2OTAzLTg5NmNmNDJiMDM3ZWFkMWUwN2Y5NDk0Y2JlZWZjODlhMmRhNDZiOGMwYjJhM2UzNzA3YjA5NjJmZGY5NGI5NmI).
### Hardware

- Raspberry Pi Zero W
- A decent power bank (with 1500 mAh you get ~2 hours with AI on)

#### Display (optional)

The display is optional if you connect to `usb0` (by using the data port on the unit) and point your browser to the web ui (see config.yml).

The supported models are:

- [Waveshare eInk Display (both V1 and V2)](https://www.waveshare.com/2.13inch-e-paper-hat.htm)
- [Pimoroni Inky pHAT](https://shop.pimoroni.com/products/inky-phat)
- [PaPiRus eInk Screen](https://uk.pi-supply.com/products/papirus-zero-epaper-screen-phat-pi-zero)

### Software

- Raspbian + [nexmon patches](https://re4son-kernel.com/re4son-pi-kernel/) for monitor mode, or any Linux with a monitor mode enabled interface (if you tune config.yml).

**Do not try with Kali on the Raspberry Pi 0 W, it is compiled without hardware floating point support and TensorFlow is simply not available for it, use Raspbian.**

#### Automatically create an image

You can use the `scripts/create_sibling.sh` script to create an - ready to flash - rasbian image with pwnagotchi.

```shell
usage: ./scripts/create_sibling.sh [OPTIONS]

  Options:
    -n <name>    # Name of the pwnagotchi (default: pwnagotchi)
    -i <file>    # Provide the path of an already downloaded raspbian image
    -o <file>    # Name of the img-file (default: pwnagotchi.img)
    -s <size>    # Size which should be added to second partition (in Gigabyte) (default: 4)
    -v <version> # Version of raspbian (Supported: latest; default: latest)
    -p           # Only run provisioning (assumes the image is already mounted)
    -d           # Only run dependencies checks
    -h           # Show this help
```

#### Host Connection Share

If you connect to the unit via `usb0` (thus using the data port), you might want to use the `scripts/linux_connection_share.sh` script to bring the interface up on your end and share internet connectivity from another interface, so you can update the unit and generally download things from the internet on it.

### UI

The UI is available either via display if installed, or via http://pwnagotchi.local:8080/ if you connect to the unit via `usb0` and set a static address on the network interface (change `pwnagotchi` with the hostname of your unit).

![ui](https://i.imgur.com/XgIrcur.png)

* **CH**: Current channel the unit is operating on or `*` when hopping on all channels.
* **APS**: Number of access points on the current channel and total visible access points.
* **UP**: Time since the unit has been activated.
* **PWND**: Number of handshakes captured in this session and number of unique networks we own at least one handshake of, from the beginning.
* **AUTO**: This indicates that the algorithm is running with AI disabled (or still loading), it disappears once the AI dependencies have been bootrapped and the neural network loaded.

#### Languages

Pwnagotchi is able to speak multiple languages!! Currently supported are:

* **english** (default)
* german

If you want to add a language use the `language.sh` script.
If you want to add for example the language **italian** you would type:

```shell
./scripts/language.sh add it
# Now make your changes to the file
# sdcard/rootfs/root/pwnagotchi/scripts/pwnagotchi/locale/it/LC_MESSAGES/voice.po
./scripts/language.sh compile it
# DONE
```

If you changed the `voice.py`- File, the translations need an update. Do it like this:

```shell
./scripts/language.sh update it
# Now make your changes to the file (changed lines are marked with "fuzzy")
# sdcard/rootfs/root/pwnagotchi/scripts/pwnagotchi/locale/it/LC_MESSAGES/voice.po
./scripts/language.sh compile it
# DONE
```

### Random Info

- `hostname` sets the unit name.
- At first boot, each unit generates a unique RSA keypair that can be used to authenticate advertising packets.
- **On a rpi0w, it'll take approximately 30 minutes to load the AI**.
- `/var/log/pwnagotchi.log` is your friend.
- if connected to a laptop via usb data port, with internet connectivity shared, magic things will happen.
- checkout the `ui.video` section of the `config.yml` - if you don't want to use a display, you can connect to it with the browser and a cable.
- If you get `[FAILED] Failed to start Remount Root and Kernel File Systems.` while booting pwnagotchi, make sure
the `PARTUUID`s for `rootfs` and `boot` partitions are the same in `/etc/fstab`. Use `sudo blkid` to find those values when you are using `create_sibling.sh`.

## License

`pwnagotchi` is made with ♥  by [@evilsocket](https://twitter.com/evilsocket) and it's released under the GPL3 license.



