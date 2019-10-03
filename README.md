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

## Why

For hackers to learn reinforcement learning, WiFi networking and have an excuse to take a walk more often. And **it's cute as f---**.

## Documentation

- [About the Project](https://github.com/evilsocket/pwnagotchi/blob/master/docs/about.md)
- [How to Install](https://github.com/evilsocket/pwnagotchi/blob/master/docs/install.md)
- [Configuration](https://github.com/evilsocket/pwnagotchi/blob/master/docs/configure.md)
- [Usage](https://github.com/evilsocket/pwnagotchi/blob/master/docs/usage.md)
- [Plugins](https://github.com/evilsocket/pwnagotchi/blob/master/docs/plugins.md)
- [Developement](https://github.com/evilsocket/pwnagotchi/blob/master/docs/dev.md)
- [FAQ](https://github.com/evilsocket/pwnagotchi/blob/master/docs/faq.md)

## Links

- [Project Slack](https://join.slack.com/t/pwnagotchi/shared_invite/enQtNzc4NzY3MDE2OTAzLTg5NmNmNDJiMDM3ZWFkMWUwN2Y5NDk0Y2JlZWZjODlhMmRhNDZiOGMwYjJhM2UzNzA3YjA5NjJmZGY5NGI5NmI)
- [Project Twitter](https://twitter.com/pwnagotchi)
- [Project Website](https://pwnagotchi.ai/)

## License

`pwnagotchi` is made with ♥  by [@evilsocket](https://twitter.com/evilsocket) and the [amazing dev team](https://github.com/evilsocket/pwnagotchi/graphs/contributors). It's released under the GPL3 license.



