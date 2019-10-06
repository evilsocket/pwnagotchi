# Configuration

Once you've [written the image file onto the SD card](https://github.com/evilsocket/pwnagotchi/blob/master/docs/install.md#flashing-an-image), there're a few steps you'll have to follow in order to configure your new Pwnagotchi properly.

## Connect to your Pwnagotchi

1. First, start with connecting the USB cable to the data port of the Raspberry Pi and the RPi to your computer. 
2. After a few seconds, the board will boot and you will see a new Ethernet interface on your host computer.
3. You'll need to configure it with a static IP address:

  - IP: `10.0.0.1`
  - Netmask: `255.255.255.0`
  - Gateway: `10.0.0.1`
  - DNS (if required): `8.8.8.8` (or whatever)

4. If everything's been configured properly, you will now be able to `ping` both `10.0.0.2` or `pwnagotchi.local` (if you haven't customized the hostname yet—if you have named your unit already, this address will be *your unit's name* + `.local`).

5. **Congratulations!** You can now connect to your unit using SSH:

```bash
ssh pi@10.0.0.2
```
##### About your SSH connection
The default password is `raspberry`; you should change it as soon as you log in for the first time by issuing the `passwd` command and selecting a new and more complex passphrase.

If you want to login directly without entering a password (recommended!), copy your SSH public key to the unit's authorized keys:

```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub pi@10.0.0.2
```

## Give your Pwnagotchi a name

You can now set a new name for your unit by [changing the hostname](https://geek-university.com/raspberry-pi/change-raspberry-pis-hostname/)!

Create the `/root/custom.yml` file (either via SSH or by directly editing the SD card contents from a computer) that will override the [default configuration](https://github.com/evilsocket/pwnagotchi/blob/master/sdcard/rootfs/root/pwnagotchi/config.yml) with your custom values.

## Choose your Pwnagotchi's language

Pwnagotchi displays its UI in English by default, but it can speak several other languages! If you're fine with English, you don't need to do anything special.

But if you want, you can change `main.lang` to one of the supported languages:

- **English** *(default)*
- German
- Dutch
- Greek
- Macedonian
- Italian
- French
- Russian
- Swedish

## Display Selection

**Set the type of display you want to use via `ui.display.type`.**
If your display does not work after changing this setting, you might need to completely remove power from the Raspberry Pi and make a clean boot.

**You can configure the refresh interval of the display via `ui.fps`.** We recommend using a slow refresh rate to avoid shortening the lifetime of your e-ink display. The default value is `0`, which will *only* refresh when changes are made to the screen.

## Host Connection Share

Want to be able to update your Pwnagotchi and access things from the internet on it? *Sure you do!*

1. Connect to the Pwnagotchi unit via `usb0` (A.K.A., using the data port).
2. Run the appropriate connection sharing script to bring the interface up on your end and share internet connectivity from another interface:

OS | Script Location
------|---------------------------
Linux | `scripts/linux_connection_share.sh`
Mac OS X | `scripts/macos_connection_share.sh`
Windows | `scripts/win_connection_share.ps1`

## Troubleshooting

##### If your network connection keeps flapping on your device connecting to your Pwnagotchi.
* Check if `usb0` (or equivalent) device is being controlled by NetworkManager. 
* You can check this via `nmcli dev status`.
