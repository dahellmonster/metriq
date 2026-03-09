#!/bin/bash

CTID=210
HOSTNAME=metriq

pct create $CTID local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst   --hostname $HOSTNAME   --cores 1   --memory 512   --rootfs local-lvm:4   --net0 name=eth0,bridge=vmbr0,ip=dhcp   --unprivileged 1

pct start $CTID

sleep 10

pct exec $CTID -- bash -c "
apt update
apt install -y curl
curl -sSL https://raw.githubusercontent.com/dahellmonster/metriq/main/install.sh | bash
"
