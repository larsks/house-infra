#!/bin/sh

# udhcpc event script for the br0 DHCP client (house-wifi client bridge).
#
# dd-wrt's own udhcpc default event script lives at /tmp/udhcpc, which is
# tmpfs and only populated for the firmware's own WAN flow -- it does not
# exist for an interface we're driving ourselves, so udhcpc reports a
# successful lease but never actually applies an address. This script is
# installed under /jffs so it survives reboots, and is passed explicitly
# via `udhcpc -s`.

env >"/tmp/udhcpc.$interface.env"

case "$1" in
bound | renew)
  ip addr flush dev "$interface"
  ip addr add "$ip/$subnet" dev "$interface"

  if [ -n "$router" ]; then
    ip route del default dev "$interface" 2>/dev/null
    for r in $router; do
      ip route add default via "$r" dev "$interface"
    done
  fi

  if [ -n "$dns" ]; then
    # /etc is dd-wrt's read-only squashfs; /etc/resolv.conf is a
    # symlink to this file, which is the one dnsmasq actually reads.
    {
      for d in $dns; do
        echo "nameserver $d"
      done
    } >/tmp/resolv.conf.$interface
    cat /tmp/resolv.conf.$interface >/tmp/resolv.conf
    rm -f /tmp/resolv.conf.$interface
  fi
  ;;
deconfig)
  ip addr flush dev "$interface"
  ip route del default dev "$interface" 2>/dev/null
  ;;
esac
