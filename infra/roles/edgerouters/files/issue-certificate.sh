#!/bin/sh

APPDIR=/config
DATADIR=$APPDIR/acme
CA_CERTIFICATE=$APPDIR/house-ca.crt

systemctl stop lighttpd
$APPDIR/acme.sh  --config-home $DATADIR \
	--issue \
	--standalone \
	-d gw.house \
	-m lars@gw.house \
	--server https://keg.house:9000/acme/acme/directory \
	--ca-bundle $APPDIR/house-ca.crt \
	--days 5 \
	"$@"

$APPDIR/acme.sh  --config-home $DATADIR \
	--install-cert \
	-d gw.house \
	--key-file $APPDIR/certs/server.key \
	--fullchain-file $APPDIR/certs/server.crt \
	--reloadcmd "cat $APPDIR/certs/server.key $APPDIR/certs/server.crt > $APPDIR/certs/server.combined && chmod 600 $APPDIR/certs/server.combined"
systemctl start lighttpd