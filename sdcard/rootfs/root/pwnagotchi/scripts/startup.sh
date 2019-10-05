#!/usr/bin/env bash

# blink 10 times to signal ready state
/usr/bin/bootblink 10 &

# start a detached screen session with bettercap
if ifconfig | grep usb0 | grep RUNNING; then
    sudo -H -u root /usr/bin/screen -dmS pwnagotchi -c /root/pwnagotchi/data/screenrc.manual
else
    sudo -H -u root /usr/bin/screen -dmS pwnagotchi -c /root/pwnagotchi/data/screenrc.auto
fi
