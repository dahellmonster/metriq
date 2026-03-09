#!/bin/bash
set -e

echo "Starting Metriq installation..."

CTID=210
HOSTNAME="metriq"
TEMPLATE="debian-12-standard_12.2-1_amd64.tar.zst"
STORAGE="local-lvm"
DISK_SIZE="4"
MEMORY="512"
CORES="1"
BRIDGE="vmbr0"

REPO="https://raw.githubusercontent.com/YOURUSER/metriq/main/install.sh"

echo "Updating Proxmox template list..."
pveam update

echo "Checking for Debian template..."

if ! pveam list local | grep -q "$TEMPLATE"; then
    echo "Downloading Debian 12 template..."
    pveam download local $TEMPLATE
fi

echo "Checking if container already exists..."

if pct list | grep -q "^$CTID "; then
    echo "Container $CTID already exists. Aborting."
    exit 1
fi

echo "Creating LXC container..."

pct create $CTID local:vztmpl/$TEMPLATE \
    --hostname $HOSTNAME \
    --cores $CORES \
    --memory $MEMORY \
    --rootfs $STORAGE:$DISK_SIZE \
    --net0 name=eth0,bridge=$BRIDGE,ip=dhcp \
    --unprivileged 1

echo "Starting container..."

pct start $CTID

echo "Waiting for container networking..."
sleep 15

echo "Installing Metriq inside container..."

pct exec $CTID -- bash -c "
apt update
apt install -y curl
curl -sSL $REPO | bash
"

echo ""
echo "Metriq installation complete."
echo ""
echo "Check container IP with:"
echo "pct exec $CTID -- ip a"
echo ""
echo "Then open:"
echo "http://CONTAINER_IP:8000/analytics"