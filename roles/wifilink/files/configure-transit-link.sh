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

if [ -z "$HOSTNAME" ]; then
  echo "ERROR: HOSTNAME is not set" >&2
  exit 1
fi

if echo "$HOSTNAME" | grep -q backhaul-1; then
  VLAN1=10.18.25.1/29
  LOCAL=100.64.64.1/29
  REMOTE=100.64.64.2/29
elif echo "$HOSTNAME" | grep -q backhaul-2; then
  VLAN1=10.18.25.2/29
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

ip link show vlan1 | grep -q 'master br0' &&
  ip link set nomaster vlan1

ip addr show br0 | grep 'inet ' &&
  ip addr flush br0

ip addr show vlan1 | grep -q $VLAN1 ||
  ip addr add $VLAN1 dev vlan1

# eth2 is normally given its address via the firmware's own
# wan_proto=static/wan_ipaddr handling, since it's a Wireless Client
# (sta) radio that dd-wrt treats as WAN. With the br0 WET radio also
# active, dd-wrt's "which client radio is WAN" bookkeeping gets
# confused and this address assignment stops happening reliably, so
# apply it ourselves instead.
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

# br0 is left to the firmware (vlan2/eth2/eth1 -- whatever dd-wrt puts
# there, including the WET client-bridge radio); give it a persistent
# DHCP client against our own event script, since /tmp/udhcpc (dd-wrt's
# default, used for its own WAN flow) does not exist for an interface
# we're driving ourselves, and a one-shot `udhcpc -q` never renews.
BR0_DHCP_PID=$(cat /var/run/udhcpc.br0.pid 2>/dev/null)
if [ -z "$BR0_DHCP_PID" ] || ! kill -0 "$BR0_DHCP_PID" 2>/dev/null; then
  udhcpc -i br0 -s /jffs/scripts/udhcpc-br0.sh -b -p /var/run/udhcpc.br0.pid
fi
