#!/bin/sh

cat >/tmp/root/.profile <<'EOF'
PATH=/opt/bin:/opt/sbin:$PATH
export PATH

PS1='\h \w # '
EOF
