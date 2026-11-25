#!/bin/sh

# Establishes the bind mount that lets snmpd-wrapper.sh patch
# /tmp/snmpd/snmpd.conf on every snmpd invocation (see that script for
# why a one-shot patch isn't enough) by overlaying it onto the real
# /usr/sbin/snmpd binary, which is stashed aside first since this path
# is the wrapper's now.
#
# Bind mounts don't survive a reboot, so the mount step has to run
# again every boot (via rc_startup); it's guarded so re-running it
# within the same boot -- pyinfra re-invokes this script whenever the
# wrapper, this script, or the pass_persist script itself changes --
# doesn't stash the wrapper on top of itself. The kill-and-relaunch
# below always runs though, since that's also how such a change gets
# picked up without waiting for a reboot or an unrelated dd-wrt
# restart to happen to come along.

REAL_BINARY=/usr/sbin/snmpd
STASHED_BINARY=/jffs/scripts/snmpd.real
WRAPPER=/jffs/scripts/snmpd-wrapper.sh

if ! grep -q " $REAL_BINARY " /proc/mounts; then
  cp "$REAL_BINARY" "$STASHED_BINARY"
  chmod +x "$STASHED_BINARY"
  mount -o bind "$WRAPPER" "$REAL_BINARY"
fi

killall snmpd 2>/dev/null
i=0
while pidof snmpd >/dev/null 2>&1; do
  i=$((i + 1))
  [ "$i" -ge 10 ] && break
  sleep 1
done

"$REAL_BINARY" -c /tmp/snmpd/snmpd.conf >/dev/null 2>&1 &
