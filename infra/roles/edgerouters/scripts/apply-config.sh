#!/bin/sh

sg vyattacfg -c '/bin/vbash -c "
export _OFR_CONFIGURE=ok
. /etc/bash_completion.d/vyatta-cfg 2>/dev/null
set -e
load /home/ubnt/config.new
if compare; then
commit
save
echo \"###CONFIG CHANGED###\"
fi
exit
"' </dev/null
