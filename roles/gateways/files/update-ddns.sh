#!/bin/sh
# dhclient exit hook shim for the DDNS update.
#
# IMPORTANT: EdgeOS's dhclient-script (Debian-derived) runs exit hooks via
# run_hookdir/run_hook, which sources each one with `. $script` -- NOT as a
# subprocess. Any `exit` in a dot-sourced script would terminate the
# CALLING shell (dhclient-script itself), not just this hook, so this file
# must never call `exit` (nor otherwise fail in a way that aborts the
# sourcing shell). The real logic lives in update-ddns-run.sh, which is
# invoked below as a genuine subprocess, so an `exit` there only ends that
# subprocess.
case "${reason:-}" in
BOUND | RENEW | REBIND | REBOOT)
  /config/scripts/update-ddns-run.sh || true
  ;;
esac
