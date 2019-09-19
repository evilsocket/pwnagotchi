# Pwnagotchi

Pwnagotchi is an "AI" that learns from the WiFi environment and instruments bettercap in order to maximize the WPA key material (any form of handshake that is crackable) captured. Specifically, it's using an [LSTM with MLP feature extractor](https://stable-baselines.readthedocs.io/en/master/modules/policies.html#stable_baselines.common.policies.MlpLstmPolicy) as its policy network for the [A2C agent](https://stable-baselines.readthedocs.io/en/master/modules/a2c.html). Here is [a very good intro](https://hackernoon.com/intuitive-rl-intro-to-advantage-actor-critic-a2c-4ff545978752) on the subject.

Instead of playing [Super Mario or Atari games](https://becominghuman.ai/getting-mario-back-into-the-gym-setting-up-super-mario-bros-in-openais-gym-8e39a96c1e41?gi=c4b66c3d5ced), pwnagotchi will tune over time [its own parameters](https://github.com/evilsocket/pwnagotchi/blob/master/sdcard/rootfs/root/pwnagotchi/config.yml#L54), effectively learning to get better at pwning WiFi things.

If you are a boring person, you can disable the AI and have the algorithm run just with the preconfigured default parameters.

Several states and states transitions are configurable and represented on the display as different expressions and sentences.

The software **requires bettercap compiled from master**.

## Documentation

**THIS IS STILL ALPHA STAGE SOFTWARE, IF YOU DECIDE TO TRY TO USE IT, YOU ARE ON YOUR OWN, NO SUPPORT WILL BE PROVIDED, NEITHER FOR INSTALLATION OR FOR BUGS**

### Hardware

- Raspberry Pi Zero W
- [Waveshare eInk Display](https://www.waveshare.com/2.13inch-e-paper-hat.htm) (optional if you connect to usb0 and point your browser to the web ui, see config.yml)
- A decent power bank (with 1500 mAh you get ~2 hours with AI on)

### Software

- Raspbian + nexmon patches for monitor mode, or any Linux with a monitor mode enabled interface (if you tune config.yml).

## License

`pwnagotchi` is made with ♥  by [@evilsocket](https://twitter.com/evilsocket) and it's released under the GPL3 license.



