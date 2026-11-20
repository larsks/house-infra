#!/bin/sh

APPDIR=/config
DATADIR="$APPDIR/acme"
CERTDIR="$APPDIR/certs"
CA_CERTIFICATE="$APPDIR/house-ca.crt"

mkdir -p "$DATADIR" "$CERTDIR"

systemctl stop lighttpd
trap "systemctl start lighttpd" EXIT TERM INT QUIT

$APPDIR/acme.sh --config-home $DATADIR \
  --issue \
  --standalone \
  -d gw.house \
  -m lars@gw.house \
  --server https://keg.house:9000/acme/acme/directory \
  --ca-bundle "$CA_CERTIFICATE" \
  --days 5 \
  "$@"

$APPDIR/acme.sh --config-home $DATADIR \
  --install-cert \
  -d gw.house \
  --key-file "$CERTDIR/server.key" \
  --fullchain-file "$CERTDIR/server.crt" \
  --reloadcmd "cat $CERTDIR/server.key $CERTDIR/server.crt > $CERTDIR/server.combined && chmod 600 $CERTDIR/server.combined"
