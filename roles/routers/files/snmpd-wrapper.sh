#!/bin/sh

# Bind-mounted over /usr/sbin/snmpd by configure-snmpd-wrapper.sh, so
# every snmpd invocation runs through here first -- no matter what
# triggers it. dd-wrt's own start_snmp() (see
# src/router/services/services/snmp.c) truncates and regenerates
# /tmp/snmpd/snmpd.conf from nvram on every restart, with no supported
# way to add extra directives, and it restarts snmpd at points we
# can't fully enumerate (observed: right after NTP sync, in addition
# to boot and the web UI's Services "Apply"). Patching the file once
# isn't enough, so this patches it on every single invocation instead.
#
# dd-wrt always invokes us as `snmpd -c /tmp/snmpd/snmpd.conf`. We
# copy that freshly (re)generated conf, append the pass_persist
# directive dd-wrt has no way to add itself, and hand the patched
# copy to the real binary -- stashed aside at $REAL, since this path
# is us now.

REAL=/jffs/scripts/snmpd.real
CONF=/tmp/snmpd/snmpd.conf
PATCHED=/tmp/snmpd/snmpd.patched.conf
LINE="pass_persist .1.3.6.1.4.1.8072.9999 /jffs/scripts/snmp-wireless-stats.lua"

if [ -f "$CONF" ]; then
  cp "$CONF" "$PATCHED"
else
  : >"$PATCHED"
fi
grep -qxF "$LINE" "$PATCHED" || echo "$LINE" >>"$PATCHED"

exec "$REAL" -c "$PATCHED"
