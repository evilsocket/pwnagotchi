## About the Project

[Pwnagotchi](https://twitter.com/pwnagotchi) is an [A2C](https://hackernoon.com/intuitive-rl-intro-to-advantage-actor-critic-a2c-4ff545978752)-based "AI" leveraging [bettercap](https://www.bettercap.org/) that learns from its surrounding WiFi environment in order to maximize the WPA key material it captures (either passively, or by performing deauthentication and association attacks). This material is collected as PCAP files containing any form of handshake supported by [hashcat](https://hashcat.net/hashcat/), including [PMKIDs](https://www.evilsocket.net/2019/02/13/Pwning-WiFi-networks-with-bettercap-and-the-PMKID-client-less-attack/), 
full and half WPA handshakes.

![handshake](https://i.imgur.com/pdA4vCZ.png)

Instead of merely playing [Super Mario or Atari games](https://becominghuman.ai/getting-mario-back-into-the-gym-setting-up-super-mario-bros-in-openais-gym-8e39a96c1e41?gi=c4b66c3d5ced) like most reinforcement learning based "AI" *(yawn)*, Pwnagotchi tunes [its own parameters](https://github.com/evilsocket/pwnagotchi/blob/master/sdcard/rootfs/root/pwnagotchi/config.yml#L54) over time to **get better at pwning WiFi things** in the environments you expose it to. 

**Keep in mind:** Unlike the usual RL simulations, Pwnagotchi actually learns over time. Time for a Pwnagotchi is measured in epochs; a single epoch can last from a few seconds to minutes, depending on how many access points and client stations are visible. Do not expect your Pwnagotchi to perform amazingly well at the very beginning, as it will be [exploring](https://hackernoon.com/intuitive-rl-intro-to-advantage-actor-critic-a2c-4ff545978752) several combinations of [key parameters](https://github.com/evilsocket/pwnagotchi/blob/master/docs/usage.md#training-the-ai) to determine ideal adjustments for pwning the particular environment you are exposing it to during its beginning epochs ... but **definitely listen to your pwnagotchi when it tells you it's bored!** Bring it into novel WiFi environments with you and have it observe new networks and capture new handshakes—and you'll see. :)

Multiple units within close physical proximity can "talk" to each other, advertising their own presence to each other by broadcasting custom information elements using a parasite protocol I've built on top of the existing dot11 standard. Over time, two or more units trained together will learn to cooperate upon detecting each other's presence by dividing the available channels among them for optimal pwnage.

![peers](https://i.imgur.com/Ywr5aqx.png)

[Depending on the status of the unit](), several states and states transitions are configurable and represented on the display as different moods, expressions and sentences. Pwnagotchi speaks [many languages](https://github.com/evilsocket/pwnagotchi/blob/master/docs/configure.md#configuration), too!

Of course, it is possible to run your Pwnagotchi with the AI disabled (configurable in `config.yml`). Why might you want to do this? Perhaps you simply want to use your own fixed parameters (instead of letting the AI decide for you), or maybe you want to save battery and CPU cycles, or maybe it's just you have strong concerns about aiding and abetting baby Skynet. Whatever your particular reasons may be: an AI-disabled Pwnagotchi is still a simple and very effective automated deauther, WPA handshake sniffer, and portable [bettercap](https://www.bettercap.org/) + [webui](https://github.com/evilsocket/pwnagotchi/blob/master/docs/usage.md#bettercaps-web-ui) dedicated hardware.


## License

`pwnagotchi` is made with ♥  by [@evilsocket](https://twitter.com/evilsocket) and the [amazing dev team](https://github.com/evilsocket/pwnagotchi/graphs/contributors). It's released under the GPL3 license.
