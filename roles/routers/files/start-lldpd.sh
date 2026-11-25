#!/bin/sh

LLDPD=/opt/sbin/lldpd
DD_BOARD=$(nvram get DD_BOARD)
DD_VERSION=$(nvram get os_version)
OS_NAME=$(uname -s || echo Linux)
OS_MACHINE=$(uname -m || echo unknown)

if [ -x $LLDPD ]; then
  $LLDPD -I vlan1 -S "DD-WRT ${DD_VERSION:-unknown} on ${DD_BOARD:-unknown}" -P "${OS_NAME} ${OS_MACHINE}"
fi
