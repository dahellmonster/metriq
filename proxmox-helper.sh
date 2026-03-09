#!/usr/bin/env bash
set -e

clear

echo "======================================"
echo "         Metriq Installer"
echo "   Personal Health Analytics Engine"
echo "======================================"
echo ""

echo "Updating template list..."
pveam update >/dev/null

echo "Finding latest Debian 12 template..."

TEMPLATE=$(pveam available | grep debian-12-standard | awk '{print $2}' | tail -n1)

if [ -z "$TEMPLATE" ]; then
    echo "Could not find a Debian 12 template."
    exit 1
fi

echo "Latest template: $TEMPLATE"

echo ""
echo "Checking if template is already downloaded..."

if ! pveam list local | grep -q "$TEMPLATE"; then
    echo "Downloading template..."
    pveam download local $TEMPLATE
else
    echo "Template already exists."
fi

echo ""
echo "Finding next available CTID..."

CTID=$(pvesh get /cluster/nextid)

echo "Using CTID: $CTID"

HOSTNAME="metriq"
STORAGE="local-lvm"

echo ""
echo "Creating Metriq container..."

pct create $CTID local:vztmpl/$TEMPLATE \
  --hostname $HOSTNAME \
  --cores 1 \
  --memory 512 \
  --rootfs $STORAGE:4 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --unprivileged 1

echo ""
echo "Starting container..."

pct start $CTID

echo "Waiting for networking..."
sleep 15

echo ""
echo "Installing Metriq..."

pct exec $CTID -- bash -c "
apt update
apt install -y curl git
curl -sSL https://raw.githubusercontent.com/dahellmonster/metriq/main/install.sh | bash
"

echo ""
echo "======================================"
echo "       Metriq Installation Complete"
echo "======================================"
echo ""

IP=$(pct exec $CTID -- hostname -I | awk '{print $1}')

echo "Container ID : $CTID"
echo "Container IP : $IP"
echo ""

echo "Open Metriq API at:"
echo "http://$IP:8000/analytics"
echo ""