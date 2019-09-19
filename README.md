# Pwnagotchi

[Pwnagotchi](https://twitter.com/pwnagotchi) is an "AI" that learns from the WiFi environment and instruments bettercap in order to maximize the WPA key material (any form of handshake that is crackable, including [PMKIDs](https://www.evilsocket.net/2019/02/13/Pwning-WiFi-networks-with-bettercap-and-the-PMKID-client-less-attack/), full and half WPA handshakes) captured. 

Specifically, it's using an [LSTM with MLP feature extractor](https://stable-baselines.readthedocs.io/en/master/modules/policies.html#stable_baselines.common.policies.MlpLstmPolicy) as its policy network for the [A2C agent](https://stable-baselines.readthedocs.io/en/master/modules/a2c.html), here is [a very good intro](https://hackernoon.com/intuitive-rl-intro-to-advantage-actor-critic-a2c-4ff545978752) on the subject.

Instead of playing [Super Mario or Atari games](https://becominghuman.ai/getting-mario-back-into-the-gym-setting-up-super-mario-bros-in-openais-gym-8e39a96c1e41?gi=c4b66c3d5ced), pwnagotchi will tune over time [its own parameters](https://github.com/evilsocket/pwnagotchi/blob/master/sdcard/rootfs/root/pwnagotchi/config.yml#L54), effectively learning to get better at pwning WiFi things. **Keep in mind:** unlike the usual RL simulations, pwnagotchi learns over time (where a single epoch can last from a few seconds to minutes, depending on how many access points and client stations are visible), do not expect it to perform amazingly well at the beginning, as it'll be exploring several combinations of parameters ... but listen to it when it's bored, bring it with you and have it observe new networks and capture new handshakes and you'll see :)

Multiple units can talk to each other, advertising their own presence using a parasite protocol I've built on top of the existing dot11 standard, by broadcasting custom information elements. Over time, two or more units learn to cooperate if they detect each other's presence, by dividing the available channels among them.

Several states and states transitions are configurable and represented on the display as different expressions and sentences.

If instead you are a boring person, you can disable the AI and have the algorithm run just with the preconfigured default parameters and enjoy a very portable bettercap + webui dedicated hardware.

**NOTE:** The software **requires bettercap compiled from master**.

![units](https://imgur.com/MStjXZF)

## Why

For hackers to learn reinforcement learning, WiFi networking and have an excuse to take a walk more often. And **it's cute as f---**.

## Documentation

**THIS IS STILL ALPHA STAGE SOFTWARE, IF YOU DECIDE TO TRY TO USE IT, YOU ARE ON YOUR OWN, NO SUPPORT WILL BE PROVIDED, NEITHER FOR INSTALLATION OR FOR BUGS**

### Hardware

- Raspberry Pi Zero W
- [Waveshare eInk Display](https://www.waveshare.com/2.13inch-e-paper-hat.htm) (optional if you connect to usb0 and point your browser to the web ui, see config.yml)
- A decent power bank (with 1500 mAh you get ~2 hours with AI on)

### Software

- Raspbian + nexmon patches for monitor mode, or any Linux with a monitor mode enabled interface (if you tune config.yml).

### Random Info

- `hostname` sets the unit name.
- At first boot, each unit generates a unique RSA keypair that can be used to authenticate advertising packets.
- **On a rpi0w, it'll take approximately 30 minutes to load the AI**.
- `/var/log/pwnagotchi.log` is your friend.
- if connected to a laptop via usb data port, with internet connectivity shared, magic things will happen.

Magic scripts that makes it talk to the internet:

```sh
#!/bin/bash

# name of the ethernet gadget interface on the host
USB_IFACE=${1:-enp0s20f0u1}
USB_IFACE_IP=10.0.0.1
USB_IFACE_NET=10.0.0.0/24
# host interface to use for upstream connection
UPSTREAM_IFACE=enxe4b97aa99867

ip addr add $USB_IFACE_IP/24 dev $USB_IFACE
ifconfig $USB_IFACE up

iptables -A FORWARD -o $UPSTREAM_IFACE -i $USB_IFACE -s $USB_IFACE_NET -m conntrack --ctstate NEW -j ACCEPT
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -t nat -F POSTROUTING
iptables -t nat -A POSTROUTING -o $UPSTREAM_IFACE -j MASQUERADE

echo 1 > /proc/sys/net/ipv4/ip_forward
```

## License

`pwnagotchi` is made with ♥  by [@evilsocket](https://twitter.com/evilsocket) and it's released under the GPL3 license.



