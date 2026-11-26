#!/bin/sh
# Notifies the update-ddns-record Lambda of a WAN IP change so it can UPSERT
# the house.dyn.oddbit.com Route53 record.
#
# This is the real worker script. It is invoked as a genuine subprocess by
# the dot-sourced dhclient-exit-hooks.d/update-ddns shim (update-ddns.sh in
# this directory) -- never source this file directly, since it uses `exit`
# freely and relies on running in its own process.
#
# Invoked with old_ip_address/new_ip_address exported. Mirrors the env-var
# contract of the 2022 Python client it replaces:
#   DDNS_URL               base URL of the update-ddns-record Lambda
#   DDNS_HOSTNAME          hostname to update (sent as the "hostname" param)
#   DDNS_TOKEN             shared secret token (sent as the "token" param)
#   DDNS_TOKEN_FILE        path to read the token from, if DDNS_TOKEN is unset
#   DDNS_FORCE             if set/non-empty, always update
#   DDNS_MAX_INTERVAL      max seconds between updates even if IP is
#                          unchanged (default 86400)
#   DDNS_LAST_UPDATE_FILE  path recording the epoch time of the last
#                          successful update (default /run/ddns_last_update)
#
# The Lambda returns a real HTTP status (2xx on success, 4xx/5xx on
# failure), so curl's --fail flag alone tells success from failure -- no
# JSON body parsing needed (there's no jq on BusyBox ash anyway).

PROGNAME=${0##*/}

log() {
  printf "%s: %s\n" "$PROGNAME" "$*" | logger -s
}

die() {
  log "ERROR: $*"
  exit 1
}

if [ -f /config/auth/ddns.env ]; then
  . /config/auth/ddns.env
fi

DDNS_MAX_INTERVAL="${DDNS_MAX_INTERVAL:-86400}"
DDNS_LAST_UPDATE_FILE="${DDNS_LAST_UPDATE_FILE:-/run/ddns_last_update}"

if [ -z "$DDNS_TOKEN" ]; then
  die "DDNS_TOKEN is not set"
fi

if [ -z "${DDNS_HOSTNAME:-}" ]; then
  die "DDNS_HOSTNAME is not set"
fi

if [ -z "${DDNS_URL:-}" ]; then
  die "DDNS_URL is not set"
fi

# Decide whether an update is due.
SHOULD_UPDATE=0

if [ "${old_ip_address:-}" != "${new_ip_address:-}" ]; then
  log "will update $DDNS_HOSTNAME: address has changed ($old_ip_address != $new_ip_address)"
  SHOULD_UPDATE=1
fi

if [ -n "${DDNS_FORCE:-}" ]; then
  log "will update $DDNS_HOSTNAME: forcing change due to DDNS_FORCE"
  SHOULD_UPDATE=1
fi

if [ "$SHOULD_UPDATE" -eq 0 ]; then
  LAST_UPDATE=$(cat "$DDNS_LAST_UPDATE_FILE" 2>/dev/null)
  case "$LAST_UPDATE" in
  '' | *[!0-9]*)
    # missing or unparseable -> treat as "update due"
    log "will update $DDNS_HOSTNAME: $DDNS_LAST_UPDATE_FILE missing or unreadable"
    SHOULD_UPDATE=1
    ;;
  *)
    NOW=$(date +%s)
    ELAPSED=$((NOW - LAST_UPDATE))
    if [ "$ELAPSED" -ge "$DDNS_MAX_INTERVAL" ]; then
      log "will update $DDNS_HOSTNAME: more than $DDNS_MAX_INTERVAL seconds since last change"
      SHOULD_UPDATE=1
    fi
    ;;
  esac
fi

if [ "$SHOULD_UPDATE" -eq 0 ]; then
  log "no update required"
  exit 0
fi

# --max-time bounds how long a stalled/unreachable endpoint can block
# dhclient (which waits on this hook). --fail makes curl exit non-zero on
# an HTTP error status (4xx/5xx), which is now the sole success/failure
# signal -- no response-body parsing needed.
RESPONSE=$(curl -s --max-time 15 --fail "$DDNS_URL?hostname=$DDNS_HOSTNAME&token=$DDNS_TOKEN")
CURL_STATUS=$?

if [ "$CURL_STATUS" -ne 0 ]; then
  die "curl failed with status $CURL_STATUS: $RESPONSE"
fi

log "successfully updated $DDNS_HOSTNAME to $new_ip_address"
date +%s >"$DDNS_LAST_UPDATE_FILE"
