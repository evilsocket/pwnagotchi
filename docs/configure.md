### Connecting to your Pwnagotchi

Once you wrote the image file on the SD card, there're a few steps you'll have to follow in order to configure your unit properly, first, start with connecting the USB cable to the 
data port of the Raspberry Pi and the RPi to your computer. After a few seconds the board will boot and you will see a new Ethernet interface on your host computer.

You'll need to configure it with a static IP address:

- IP: `10.0.0.2`
- Netmask: `255.255.255.0`
- Gateway: `10.0.0.1`
- DNS (if required): `8.8.8.8` (or whatever)

If everything's been configured properly, you will now be able to `ping` both `10.0.0.2` or `pwnagotchi.local` (if you haven't customized the hostname yet).

You can now connect to your unit using SSH:

```bash
ssh pi@10.0.0.2
```

The default password is `raspberry`, you should change it as soon as you log in for the first time by issuing the `passwd`command and selecting a new and more complex passphrase.

Moreover, it is recommended that you copy your SSH public key among the unit's authorized ones, so you can directly log in without entering a password:

```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub pi@10.0.0.2
```

### Configuration

You can now set a new name for your unit by [changing the hostname](https://geek-university.com/raspberry-pi/change-raspberry-pis-hostname/). Create the `/root/custom.yml` file (either via SSH or by direclty editing the SD card contents from a computer) that will override 
the [default configuration](https://github.com/evilsocket/pwnagotchi/blob/master/sdcard/rootfs/root/pwnagotchi/config.yml) with your custom values.

For instance, you can change `main.lang` to one of the supported languages:

* **english** (default)
* german
* dutch
* greek
* macedonian
* italian
* french

The set the type of display you want to use via `ui.display.type` (if your display does not work after changing this setting, you might need to complete remove power from the Raspberry and make a clean boot).

You can configure the refresh interval of the display via `ui.fps`, we advise to use a slow refresh to not shorten the lifetime of your display. The default value is 0, which will only refresh when changes are made to the screen.

### Host Connection Share

If you connect to the unit via `usb0` (thus using the data port), you might want to use the `scripts/linux_connection_share.sh` or 
 `scripts/macos_connection_share.sh` script to bring the interface up on your end and share internet connectivity from another interface, so you can update the unit and generally download things from the internet on it.