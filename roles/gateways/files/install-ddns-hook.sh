#!/bin/sh
# post-config.d script: EdgeOS resets /etc on every boot (only /config
# persists across reboots/firmware upgrades), so the dhclient exit hook
# shim has to be re-copied into /etc/dhcp3/dhclient-exit-hooks.d/ every
# time the router comes up. EdgeOS runs every executable file under
# /config/scripts/post-config.d/ automatically after it finishes applying
# config.boot on boot, which is what re-installs it here.
#
# The canonical copy of the shim lives at /config/scripts/update-ddns.sh
# (persistent); this script just (re)installs it into its real,
# non-persistent location.

set -e

mkdir -p /etc/dhcp3/dhclient-exit-hooks.d
cp /config/scripts/update-ddns.sh /etc/dhcp3/dhclient-exit-hooks.d/update-ddns
chmod 755 /etc/dhcp3/dhclient-exit-hooks.d/update-ddns
