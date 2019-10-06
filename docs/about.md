# About the Project

[Pwnagotchi](https://twitter.com/pwnagotchi) is an [A2C](https://hackernoon.com/intuitive-rl-intro-to-advantage-actor-critic-a2c-4ff545978752)-based "AI" leveraging [bettercap](https://www.bettercap.org/) that learns from its surrounding WiFi environment in order to maximize the WPA key material it captures (either passively, or by performing deauthentication and association attacks). This material is collected as PCAP files containing any form of handshake supported by [hashcat](https://hashcat.net/hashcat/), including [PMKIDs](https://www.evilsocket.net/2019/02/13/Pwning-WiFi-networks-with-bettercap-and-the-PMKID-client-less-attack/), 
full and half WPA handshakes.

![handshake](https://i.imgur.com/pdA4vCZ.png)

Instead of merely playing [Super Mario or Atari games](https://becominghuman.ai/getting-mario-back-into-the-gym-setting-up-super-mario-bros-in-openais-gym-8e39a96c1e41?gi=c4b66c3d5ced) like most reinforcement learning based "AI" *(yawn)*, Pwnagotchi tunes [its own parameters](https://github.com/evilsocket/pwnagotchi/blob/master/sdcard/rootfs/root/pwnagotchi/config.yml#L54) over time to **get better at pwning WiFi things** in the environments you expose it to. 

**Keep in mind:** Unlike the usual RL simulations, Pwnagotchi actually learns over time. Time for a Pwnagotchi is measured in epochs; a single epoch can last from a few seconds to minutes, depending on how many access points and client stations are visible. Do not expect your Pwnagotchi to perform amazingly well at the very beginning, as it will be [exploring](https://hackernoon.com/intuitive-rl-intro-to-advantage-actor-critic-a2c-4ff545978752) several combinations of [key parameters](https://github.com/evilsocket/pwnagotchi/blob/master/docs/usage.md#training-the-ai) to determine ideal adjustments for pwning the particular environment you are exposing it to during its beginning epochs ... but **definitely listen to your pwnagotchi when it tells you it's bored!** Bring it into novel WiFi environments with you and have it observe new networks and capture new handshakes—and you'll see. :)

Multiple units within close physical proximity can "talk" to each other, advertising their own presence to each other by broadcasting custom information elements using a parasite protocol I've built on top of the existing dot11 standard. Over time, two or more units trained together will learn to cooperate upon detecting each other's presence by dividing the available channels among them for optimal pwnage.

![peers](https://i.imgur.com/Ywr5aqx.png)

[Depending on the status of the unit](), several states and states transitions are configurable and represented on the display as different moods, expressions and sentences. Pwnagotchi speaks [many languages](https://github.com/evilsocket/pwnagotchi/blob/master/docs/configure.md#configuration), too!

Of course, it is possible to run your Pwnagotchi with the AI disabled (configurable in `config.yml`). Why might you want to do this? Perhaps you simply want to use your own fixed parameters (instead of letting the AI decide for you), or maybe you want to save battery and CPU cycles, or maybe it's just you have strong concerns about aiding and abetting baby Skynet. Whatever your particular reasons may be: an AI-disabled Pwnagotchi is still a simple and very effective automated deauther, WPA handshake sniffer, and portable [bettercap](https://www.bettercap.org/) + [webui](https://github.com/evilsocket/pwnagotchi/blob/master/docs/usage.md#bettercaps-web-ui) dedicated hardware.

## WiFi Handshakes 101

In order to understand why it's valuable to have an AI that wants to eat handshakes, it's helpful to understand a little bit about how handshakes are used in the WPA/WPA2 wireless protocol.

Before a client device that's connecting to a wireless access point—say, for instance, your phone connecting to your home WiFi network—is able to securely transmit to and receive data from that access point, a process called the **4-Way Handshake** needs to happen in order for the WPA encryption keys to be generated. This process consists of the exchange of four packets (hence the "4" in "4-Way") between the client device and the AP; these are used to derive session keys from the access point's WiFi password. Once the packets are successfully exchanged and the keys have been generated, the client device is authenticated and can start sending and receiving data packets to and from the wireless AP that are secured by encryption.

<p align="center">
<img src="https://i.imgur.com/nI8IE6a.png"/>
<br/>
<small>image taken from <a target="_blank" href="https://www.wifi-professionals.com/2019/01/4-way-handshake">wifi-professionals.com</a></small>
</p>

So...what's the catch? Well, these four packets can easily be "sniffed" by an attacker monitoring nearby (say, with a Pwnagotchi :innocent:). And once recorded, that attacker can use [dictionary and/or bruteforce attacks](https://hashcat.net/wiki/doku.php?id=cracking_wpawpa2) to crack the handshakes and recover the original WiFi key. In fact, **successful recovery of the WiFi key doesn't necessarily even need all four packets!** A half-handshake (containing only two of the four packets) can be cracked, too—and in some *(most)* cases, just [a single packet is enough](https://hashcat.net/forum/thread-7717-post-41447.html), *even without clients.*

In order to ~~eat~~ collect as many of these crackable handshake packets as possible, Pwnagotchi uses two strategies:

- **Deauthenticating the client stations it detects.** A deauthenticated device must reauthenticate to its access point by re-performing the 4-Way Handshake with the AP, thereby giving Pwnagotchi another chance to sniff the handshake packets and collect more crackable material.
- **Send association frames directly to the access points themselves**
to try to force them to [leak the PMKID](https://www.evilsocket.net/2019/02/13/Pwning-WiFi-networks-with-bettercap-and-the-PMKID-client-less-attack/).

All the handshakes captured this way are saved into `.pcap` files on Pwnagotchi's filesystem. Each PCAP file that Pwnagotchi generates is organized according to access point; one PCAP will contain all the handshakes that Pwnagotchi has ever captured for that particular AP. These handshakes can later be [cracked with proper hardware and software](https://hashcat.net/wiki/doku.php?id=cracking_wpawpa2).

## License

`pwnagotchi` is made with ♥  by [@evilsocket](https://twitter.com/evilsocket) and the [amazing dev team](https://github.com/evilsocket/pwnagotchi/graphs/contributors). It's released under the GPL3 license.
