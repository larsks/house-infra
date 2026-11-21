#!/bin/sh

APPDIR=/volume1/scripts
CA_CERTIFICATE=$APPDIR/house-ca.crt
ACME_CONFIG_HOME="$APPDIR/data/acme"

$APPDIR/acme.sh --server https://keg.house:9000/acme/acme/directory \
  --config-home "$ACME_CONFIG_HOME" \
  --webroot /var/lib/letsencrypt \
  -m lars@keg.house -d keg.house \
  --ca-bundle "$CA_CERTIFICATE" \
  --issue \
  "$@"

SYNO_USE_TEMP_ADMIN=1 \
  $APPDIR/acme.sh \
  --config-home "$ACME_CONFIG_HOME" \
  -d keg.house \
  --deploy --deploy-hook synology_dsm
