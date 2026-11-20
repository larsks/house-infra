#!/bin/sh

APPDIR=/config
DATADIR=$APPDIR/acme
CA_CERTIFICATE=$APPDIR/house-ca.crt

systemctl stop lighttpd
$APPDIR/acme.sh  --no-color --syslog 6 --config-home $DATADIR  --cron
systemctl start lighttpd
