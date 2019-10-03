#!/usr/bin/env bash

# name of the ethernet gadget interface on the host
USB_IFACE=${1:-en8}
# host interface to use for upstream connection
UPSTREAM_IFACE=${2:-en7}

sysctl -w net.inet.ip.forwarding=1
pfctl -e
echo "nat on ${UPSTREAM_IFACE} from ${USB_IFACE}:network to any -> (${UPSTREAM_IFACE})" | pfctl -f -
