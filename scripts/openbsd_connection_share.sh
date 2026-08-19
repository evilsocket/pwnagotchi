#!/bin/sh

USB_IFACE=$(ifconfig urndis0 | grep urndis0 | awk '{print $1}' | tr -d ':')
USB_IP=${2:-10.0.0.1}

if test $(whoami) != root; then
	doas "$0" "$@"
	exit $?
fi

if [ "${USB_IFACE}" == "urndis0" ]; then
  ifconfig ${USB_IFACE} down > /dev/null 2>&1
  ifconfig veb10 del vport10 > /dev/null 2>&1
  ifconfig veb10 destroy > /dev/null 2>&1
  ifconfig vport10 destroy > /dev/null 2>&1
  ifconfig veb10 create && ifconfig veb10 up
  ifconfig vport10 create && ifconfig vport10 up
  ifconfig vport10 ${USB_IP}      && \
  ifconfig veb10 add vport10      && \
  ifconfig veb10 add ${USB_IFACE} && \
  ifconfig ${USB_IFACE} up        && \
  sysctl -w net.inet.ip.forwarding=1
  echo "match out log on egress from vport10:network to any nat-to (egress)" | pfctl -f -
  echo "sharing connecting from upstream interface to usb interface ${USB_IFACE} ..."
  printf "Now you should be able to do: ssh pi@10.0.0.2\n"
else
  echo "can't find usb interface with ip $USB_IP"
  exit 1
fi
