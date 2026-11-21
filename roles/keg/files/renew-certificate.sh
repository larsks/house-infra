#!/bin/sh

APPDIR=/volume1/scripts
ACME_CONFIG_HOME="$APPDIR/data/acme"
$APPDIR/acme.sh --no-color --syslog 6 --config-home "$ACME_CONFIG_HOME" --cron "$@"
