#!/usr/bin/env bash

#prompt user to input pwnagotchi ethernet interface on host and input host internet interface
read -p 'Input pwnagotchi ethernet interface ex:"enp0s20f0u1": ' pwninterface
read -p 'Input host internet connected interface ex:"wlan0": ' hostinterface

# name of the ethernet gadget interface on the host
USB_IFACE=${1:-$pwninterface}
USB_IFACE_IP=10.0.0.1
USB_IFACE_NET=10.0.0.0/24
# host interface to use for upstream connection
UPSTREAM_IFACE=${2:-$hostinterface}

ip addr add "$USB_IFACE_IP/24" dev "$USB_IFACE"
ip link set "$USB_IFACE" up

iptables -A FORWARD -o "$UPSTREAM_IFACE" -i "$USB_IFACE" -s "$USB_IFACE_NET" -m conntrack --ctstate NEW -j ACCEPT
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -t nat -F POSTROUTING
iptables -t nat -A POSTROUTING -o "$UPSTREAM_IFACE" -j MASQUERADE

echo 1 > /proc/sys/net/ipv4/ip_forward
