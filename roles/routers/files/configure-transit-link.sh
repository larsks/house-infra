#!/bin/sh

# Trunk VLANs over a VXLAN tunnel between two DD-WRT routers, and give
# each router a management-only path onto the house wifi.
#
# ┌────────────┐                   ┌────────────┐
# │  switch-1  │                   │  switch-2  │
# └─┬──────────┘                   └─┬──────────┘
#   │                                │
#  eth0                             eth0
# ┌─┴────────────┐                 ┌─┴────────────┐
# │  backhaul-1  ├eth2─────────eth2┤  backhaul-2  │
# └──────────────┘      vxlan      └──────────────┘
#                       over
#                       wifi
#
# eth0+transit (the VLAN trunk) live on their own "trunk0" bridge rather
# than the firmware's br0, because dd-wrt hardcodes any wireless Client
# Bridge (WET) radio onto br0 -- there's no way to keep a WET radio off
# of it, so the trunk has to be the one that moves instead.
#
# This script runs before firewall configuration. Use rc_firewall if you
# need to modify the firewall.

addr() {
  echo "$1" | cut -f1 -d/
}

mark() {
  echo "=== START $* ==="
  "$@"
  echo "=== END $* ==="
  echo
}

dump_config() {
  mark brctl show
  mark ip addr show
  mark ip route show
  mark iptables -S
  mark iptables -t nat -S
}

if [ -z "$HOSTNAME" ]; then
  echo "ERROR: HOSTNAME is not set" >&2
  exit 1
fi

if echo "$HOSTNAME" | grep -q backhaul-1; then
  LOCAL=100.64.64.1/29
  REMOTE=100.64.64.2/29
elif echo "$HOSTNAME" | grep -q backhaul-2; then
  LOCAL=100.64.64.2/29
  REMOTE=100.64.64.1/29
else
  echo "ERROR: unknown device" >&2
  exit 1
fi

modprobe vxlan

swconfig dev switch0 vlan 1 set ports '1 2 3 4 5t'
for vlan in $(nvram get trunk_vlans); do
  swconfig dev switch0 vlan "$vlan" set ports '4t 5t'
done
swconfig dev switch0 set enable_jumbo 1
swconfig dev switch0 set enable_vlan 1
swconfig dev switch0 set apply

dump_config >/tmp/network.before

ip addr show eth2 | grep -q "$LOCAL" ||
  ip addr add "$LOCAL" dev eth2

# Increase MTU to account for vxlan metadata
ip link set mtu 1600 eth2

ip link show trunk0 >/dev/null 2>&1 || {
  ip link add trunk0 type bridge
  ip link set trunk0 up
}

ip link show transit >/dev/null 2>&1 ||
  ip link add transit type vxlan id 1825 dstport 4789 local "$(addr $LOCAL)" remote "$(addr $REMOTE)"

ip link show transit | grep -q 'master trunk0' ||
  ip link set master trunk0 transit

ip link show eth0 | grep -q 'master trunk0' || {
  ip link set nomaster eth0 2>/dev/null
  ip link set master trunk0 eth0
}

ip link set transit up

dump_config >/tmp/network.after
