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

---
### Pwnagotchi face via Bluetooth
Last tested on | Pwnagotchi version | Working? | Reference
---------------|--------------------|----------|-----------|
2019 October 6 | Unknown | :white_check_mark: | on Android
2019 October 6 | Unknown | :white_check_mark: | on iPad iOS 9.3.5

A way to view your Pwnagotchi's ~~face~~ UI wirelessly via Bluetooth on a separate device. Refresh rate is the same as the e-ink display (every few seconds). This is NOT Bluetooth tethering; this is only Bluetooth as a server on pi side; you connect the Bluetooth and get a DHCP IP address and that's it. This hack cannot leverage the data connection.

Contributed by Systemic in the Slack.

##### 1. First Step
- Comment out the Bluetooth disable line from `/boot/config.txt` : `#dtoverlay=pi3-disable-bt`
- Change `/root/pwnagotchi/config.yml` to have `0.0.0.0` instead of `10.0.0.2` to listen as well on Bluetooth.
- Then launch the following commands:

##### 2. Install required packages.

```sudo apt-get install bluez bluez-tools bridge-utils dnsmasq```

##### 3. Configure Bluetooth and start it.
```sudo modprobe bnep
sudo brctl addbr pan0
sudo brctl setfd pan0 0
sudo brctl stp pan0 off
sudo ifconfig pan0 172.26.0.1 netmask 255.255.255.0
sudo ip link set pan0 up
```

```cat <<- EOF > /tmp/dnsmasq_bt.conf```

```bind-interfaces
port=0
interface=pan0
listen-address=172.26.0.1
dhcp-range=172.26.0.2,172.26.0.100,255.255.255.0,5m
dhcp-leasefile=/tmp/dnsmasq_bt.leases
dhcp-authoritative
log-dhcp
```

```EOF```

```sudo dnsmasq -C /tmp/dnsmasq_bt.conf
sudo bt-agent -c NoInputNoOutput&
sudo bt-adapter -a hci0 --set Discoverable 1
sudo bt-adapter -a hci0 --set DiscoverableTimeout 0
sudo bt-adapter -a hci0 --set Pairable 1
sudo bt-adapter -a hci0 --set PairableTimeout 0
sudo bt-network -a hci0 -s nap pan0 &
```

##### 4. Finally: on your phone, you have to disable all existing interfaces:

- Shutdown WiFi.
- Shutdown mobile data.
- Connect to the newly available Bluetooth device (which has the name of your Pwnagotchi).
   - Once connected, you can test: `http://172.26.0.1:8080`
- You can also install bettercap's UI (`sudo bettercap` then `ui.update`) 
   - You'll need to change the http caplets to change `127.0.0.1` to `0.0.0.0`.
- You can connect to the shell with a terminal emulator ...

Happy tweaking.
