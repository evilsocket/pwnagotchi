# Pwnagotchi

<p align="center">
  <p align="center">
    <a href="https://github.com/evilsocket/pwnagotchi/releases/latest"><img alt="Release" src="https://img.shields.io/github/release/evilsocket/pwnagotchi.svg?style=flat-square"></a>
    <a href="https://github.com/evilsocket/pwnagotchi/blob/master/LICENSE.md"><img alt="Software License" src="https://img.shields.io/badge/license-GPL3-brightgreen.svg?style=flat-square"></a>
    <a href="https://github.com/evilsocket/pwnagotchi/graphs/contributors"><img alt="Contributors" src="https://img.shields.io/github/contributors/evilsocket/pwnagotchi"/></a>
    <a href="https://travis-ci.org/evilsocket/pwnagotchi"><img alt="Travis" src="https://img.shields.io/travis/evilsocket/pwnagotchi/master.svg?style=flat-square"></a>
    <a href="https://pwnagotchi.herokuapp.com/"><img alt="Slack" src="https://pwnagotchi.herokuapp.com/badge.svg"></a>
    <a href="https://twitter.com/intent/follow?screen_name=pwnagotchi"><img src="https://img.shields.io/twitter/follow/pwnagotchi?style=social&logo=twitter" alt="follow on Twitter"></a>
  </p>
</p>

[Pwnagotchi](https://twitter.com/pwnagotchi) is an [A2C](https://hackernoon.com/intuitive-rl-intro-to-advantage-actor-critic-a2c-4ff545978752)-based "AI" leveraging [bettercap](https://www.bettercap.org/) that learns from its surrounding WiFi environment in order to maximize the crackable WPA key material it captures (either passively, or by performing deauthentication and association attacks). This material is collected as PCAP files containing any form of handshake supported by [hashcat](https://hashcat.net/hashcat/), including [PMKIDs](https://www.evilsocket.net/2019/02/13/Pwning-WiFi-networks-with-bettercap-and-the-PMKID-client-less-attack/), 
full and half WPA handshakes.

![ui](https://i.imgur.com/c7xh4hN.png)

Instead of merely playing [Super Mario or Atari games](https://becominghuman.ai/getting-mario-back-into-the-gym-setting-up-super-mario-bros-in-openais-gym-8e39a96c1e41?gi=c4b66c3d5ced) like most reinforcement learning based "AI" *(yawn)*, Pwnagotchi tunes [its own parameters](https://github.com/evilsocket/pwnagotchi/blob/master/pwnagotchi/defaults.yml#L73) over time to **get better at pwning WiFi things** in the environments you expose it to. 

More specifically, Pwnagotchi is using an [LSTM with MLP feature extractor](https://stable-baselines.readthedocs.io/en/master/modules/policies.html#stable_baselines.common.policies.MlpLstmPolicy) as its policy network for the [A2C agent](https://stable-baselines.readthedocs.io/en/master/modules/a2c.html). If you're unfamiliar with A2C, here is [a very good introductory explanation](https://hackernoon.com/intuitive-rl-intro-to-advantage-actor-critic-a2c-4ff545978752) (in comic form!) of the basic principles behind how Pwnagotchi learns. (You can read more about how Pwnagotchi learns in the [Usage](https://github.com/evilsocket/pwnagotchi/blob/master/docs/usage.md#training-the-ai) doc.)

**Keep in mind:** Unlike the usual RL simulations, Pwnagotchi actually learns over time. Time for a Pwnagotchi is measured in epochs; a single epoch can last from a few seconds to minutes, depending on how many access points and client stations are visible. Do not expect your Pwnagotchi to perform amazingly well at the very beginning, as it will be [exploring](https://hackernoon.com/intuitive-rl-intro-to-advantage-actor-critic-a2c-4ff545978752) several combinations of [key parameters](https://github.com/evilsocket/pwnagotchi/blob/master/docs/usage.md#training-the-ai) to determine ideal adjustments for pwning the particular environment you are exposing it to during its beginning epochs ... but **definitely listen to your Pwnagotchi when it tells you it's bored!** Bring it into novel WiFi environments with you and have it observe new networks and capture new handshakes—and you'll see. :)

Multiple units within close physical proximity can "talk" to each other, advertising their own presence to each other by broadcasting custom information elements using a parasite protocol I've built on top of the existing dot11 standard. Over time, two or more units trained together will learn to cooperate upon detecting each other's presence by dividing the available channels among them for optimal pwnage.

## Why does Pwnagotchi exist?

For hackers to learn reinforcement learning, WiFi networking, and have an excuse to get out for more walks. Also? **It's cute as f---**.

**In case you're curious about the name:** *Pwnagotchi* is a portmanteau of *pwn* (which we shouldn't have to explain if you are interested in this project :kissing_heart:) and *-gotchi*. It is a nostalgic reference made in homage to a very popular children's toy from the 1990s called the [Tamagotchi](https://en.wikipedia.org/wiki/Tamagotchi). The Tamagotchi (たまごっち, derived from *tamago* (たまご) "egg" + *uotchi* (ウオッチ) "watch") is a cultural touchstone for many Millennial hackers as a formative electronic toy from our collective childhoods. Were you lucky enough to possess a Tamagotchi as a kid? Well, with your Pwnagotchi, you too can enjoy the nostalgic delight of being strangely emotionally attached to a handheld automata *yet again!* Except, this time around...you get to #HackThePlanet. >:D

## Documentation
---
:warning: **THE FOLLOWING DOCUMENTATION IS BEING PREPARED FOR THE v1.0 RELEASE OF PWNAGOTCHI. Since this effort is an active (and unstable) work-in-progress, the docs displayed here are in various stages of [in]completion. There will be dead links and placeholders throughout as we are still building things out in preparation for the v1.0 release.** :warning:

**IMPORTANT NOTE:** If you'd like to alphatest Pwnagotchi and are trying to get yours up and running while the project is still very unstable, please understand that the documentation here may not reflect what is currently implemented. If you have questions, ask the community of alphatesters in the [official Pwnagotchi Slack](https://pwnagotchi.herokuapp.com). The Pwnagotchi dev team is entirely focused on the v1.0 release and will NOT be providing support for alphatesters trying to get their Pwnagotchis working in the meantime. All technical support during this period of development is being provided by your fellow alphatesters in the Slack (thanks, everybody! :heart:).

https://www.pwnagotchi.ai

## Links

&nbsp; | Official Links
---------|-------
Slack | [pwnagotchi.slack.com](https://pwnagotchi.herokuapp.com)
Twitter | [@pwnagotchi](https://twitter.com/pwnagotchi)
Subreddit | [r/pwnagotchi](https://www.reddit.com/r/pwnagotchi/)
Website | [pwnagotchi.ai](https://pwnagotchi.ai/)

## License

`pwnagotchi` is made with ♥  by [@evilsocket](https://twitter.com/evilsocket) and the [amazing dev team](https://github.com/evilsocket/pwnagotchi/graphs/contributors). It is released under the GPL3 license.
