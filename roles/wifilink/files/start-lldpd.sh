#!/bin/sh

LLDPD=/opt/sbin/lldpd

if [ -x $LLDPD ]; then
  $LLDPD -I vlan1
fi
