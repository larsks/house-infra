#!/bin/sh

# udhcpc event script for the br0 DHCP client (house-wifi client bridge).
#
# dd-wrt's own udhcpc default event script lives at /tmp/udhcpc, which is
# tmpfs and only populated for the firmware's own WAN flow -- it does not
# exist for an interface we're driving ourselves, so udhcpc reports a
# successful lease but never actually applies an address. This script is
# installed under /jffs so it survives reboots, and is passed explicitly
# via `udhcpc -s`.

case "$1" in
  bound|renew)
    ip addr flush dev "$interface"
    ip addr add "$ip/$subnet" dev "$interface"
    ;;
  deconfig)
    ip addr flush dev "$interface"
    ;;
esac
