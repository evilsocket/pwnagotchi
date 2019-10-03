## About the Project

[Pwnagotchi](https://twitter.com/pwnagotchi) is an "AI" that learns from the WiFi environment and instruments 
[bettercap](https://www.bettercap.org/) in order to maximize the WPA key material that's being captured either passively
 or by performing deauthentication and association attakcs. This material is collected as pcap files containing any form 
 of handshake supported by [hashcat](https://hashcat.net/hashcat/), including [PMKIDs](https://www.evilsocket.net/2019/02/13/Pwning-WiFi-networks-with-bettercap-and-the-PMKID-client-less-attack/), 
full and half WPA handshakes.

![handshake](https://i.imgur.com/pdA4vCZ.png)

Instead of playing [Super Mario or Atari games](https://becominghuman.ai/getting-mario-back-into-the-gym-setting-up-super-mario-bros-in-openais-gym-8e39a96c1e41?gi=c4b66c3d5ced), pwnagotchi will tune over time [its own parameters](https://github.com/evilsocket/pwnagotchi/blob/master/sdcard/rootfs/root/pwnagotchi/config.yml#L54), effectively learning to get better at pwning WiFi things. **Keep in mind:** unlike the usual RL simulations, pwnagotchi learns over time (where a single epoch can last from a few seconds to minutes, depending on how many access points and client stations are visible), do not expect it to perform amazingly well at the beginning, as it'll be exploring several combinations of parameters ... but listen to it when it's bored, bring it with you and have it observe new networks and capture new handshakes and you'll see :)

Multiple units can talk to each other, advertising their own presence using a parasite protocol I've built on top of the existing dot11 standard, by broadcasting custom information elements. Over time, two or more units learn to cooperate if they detect each other's presence, by dividing the available channels among them.

![peers](https://i.imgur.com/Ywr5aqx.png)

Depending on the status of the unit, several states and states transitions are configurable and represented on the display as different moods, expressions and sentences.

If instead you just want to use your own parameters and save battery and CPU cycles, you can disable the AI in `config.yml` and enjoy an automated deauther, WPA handshake sniffer and portable bettercap + webui dedicated hardware.

## License

`pwnagotchi` is made with ♥  by [@evilsocket](https://twitter.com/evilsocket) and the [amazing dev team](https://github.com/evilsocket/pwnagotchi/graphs/contributors). It's released under the GPL3 license.