# Installation

The project has been developed to run on a Raspberry Pi 0 W configured as an [USB Ethernet gadget](https://learn.adafruit.com/turning-your-raspberry-pi-zero-into-a-usb-gadget/ethernet-gadget) device in order to connect to it via USB. 
However, given the proper configuration tweaks, any GNU/Linux computer with a WiFi interface that supports monitor mode could be used.

## Required Hardware

- [Raspberry Pi Zero W](https://www.raspberrypi.org/products/raspberry-pi-zero-w/).
- A micro SD card, 8GB recomended, **preferably of good quality and speed**.
- A decent power bank (with 1500 mAh you get ~2 hours with AI on).
- One of the supported displays (optional).

### Display

The display is an optional component as the UI is also rendered via a web interface available via the USB cable. If you connect to `usb0` (by using the data port on the unit) and point your browser to the web ui (see config.yml), your unit can work in "headless mode".

If instead you want to fully enjoy walking around and literally looking at your unit's face, the supported display models are:

- [Waveshare eInk Display (both V1 and V2)](https://www.waveshare.com/2.13inch-e-paper-hat.htm)
- [Pimoroni Inky pHAT](https://shop.pimoroni.com/products/inky-phat)
- [PaPiRus eInk Screen](https://uk.pi-supply.com/products/papirus-zero-epaper-screen-phat-pi-zero)

Needless to say, we are always happy to receive pull requests adding support for new models.

One thing to note, not all displays are created equaly, TFT displays for example work similar to an HDMI display, and they are not supported, currently all the displays supported are I2C displays.

#### Color and Black & White displays

Some of the supported displays support Black & White and Coloured versions, one common question is regarding refresh speed of said displays.

Color displays have a much slower refresh rate, in some cases it can take up to 15 seconds, if slow refresh rates is something that you want to avoid we advise you to use Black & White displays

## Flashing an Image

The easiest way to create a new Pwnagotchi is downloading the latest stable image from [our release page](https://github.com/evilsocket/pwnagotchi/releases) and write it to your SD card. You will need to use an image writing tool to install the image you have downloaded on your SD card.

[balenaEtcher](https://www.balena.io/etcher/) is a graphical SD card writing tool that works on Mac OS, Linux and Windows, 
and is the easiest option for most users. balenaEtcher also supports writing images directly from the zip file, 
without any unzipping required. To write your image with balenaEtcher:

- Download the latest [Pwnagotchi .img file](https://github.com/evilsocket/pwnagotchi/releases).
- Download [balenaEtcher](https://www.balena.io/etcher/) and install it.
- Connect an SD card reader with the SD card inside.
- Open balenaEtcher and select from your hard drive the Raspberry Pi .img or .zip file you wish to write to the SD card.
- Select the SD card you wish to write your image to.
- Review your selections and click 'Flash!' to begin writing data to the SD card.

Your SD card is now ready for the first boot!