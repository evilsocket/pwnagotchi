#!/bin/sh

USB_IFACE=$(ifconfig urndis0 | grep urndis0 | awk '{print $1}' | tr -d ':')
USB_IP=${2:-10.0.0.1}

if test $(whoami) != root; then
	doas "$0" "$@"
	exit $?
fi

if [ "${USB_IFACE}" == "urndis0" ]; then
	ifconfig ${USB_IFACE} ${USB_IP}
	sysctl -w net.inet.ip.forwarding=1
	echo "match out on egress inet from ${USB_IFACE}:network to any nat-to (egress:0)" | pfctl -f -
	pfctl -f /etc/pf.conf
	echo "sharing connecting from upstream interface to usb interface ${USB_IFACE} ..."
else
	echo "can't find usb interface with ip ${USB_IFACE}"
	exit 1
fi
