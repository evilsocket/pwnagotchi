# Unofficial Hacks
---
**IMPORTANT DISCLAIMER:** The information provided on this page is NOT officially supported by the Pwnagotchi development team. These are unofficial "hacks" that users have worked out while customizing their units and decided to document for anybody else who might want to do something similar. 

- **Please do NOT open issues if you cannot get something described in this document to work.** 
- It (almost) goes without saying, but obviously: **we are NOT responsible if you break your hardware by following any instructions documented here. Use this information at your own risk.**

---
If you test one of these hacks yourself and it still works, it's extra nice if you update the **Last Tested On** table and note any minor adjustments you may have had to make to the instructions to make it work with your particular Pwnagotchi setup. :heart:


## Screens
### Waveshare 3.5" SPI TFT screen

Last tested on | Pwnagotchi version | Working? | Reference
---------------|--------------------|----------|-----------|
2019 October 3 | Unknown | :white_check_mark: | ([link](https://github.com/evilsocket/pwnagotchi/issues/124#issue-502346040))

Some of this guide will work with other framebuffer-based displays.

- First: SSH into your Pwnagotchi, and give it some internet! 
  - Don't forget to check your default gateway and `apt-get update`.
- Follow the guide here: [www.waveshare.com/wiki/3.5inch_RPi_LCD_(A)#Method_1._Driver_installation](https://www.waveshare.com/wiki/3.5inch_RPi_LCD_(A)#Method_1._Driver_installation)
  - At the step with `./LCD35-show`, add `lite` to the command prompt (e.g., `./LCD35-show lite`).
- Reboot.
- As root, make three symlinks:
  - `cd ~`
  - `ln -s pwnagotchi.png pwnagotchi_1.png`
  - `ln -s pwnagotchi.png pwnagotchi_2.png`
  - `ln -s pwnagotchi.png pwnagotchi_3.png`
- `apt install fbi`
- Change display type to `inky` in `config.yml`
- Add `modules-load=dwc2,g_ether` to your kernel command line (`/boot/cmdline.txt`) or it will break!
- Also must add `dtoverlay=dwc2` to the bottom of (`/boot/config.txt`)
- Edit `/etc/rc.local` and add: `fbi -T 1 -a -noverbose -t 15 -cachemem 0 /root/pwnagotchi_1.png /root/pwnagotchi_2.png /root/pwnagotchi_3.png &`
- Reboot.

And you should be good!
