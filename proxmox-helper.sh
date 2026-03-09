#!/usr/bin/env bash

clear

echo "======================================="
echo "        Metriq Installer"
echo "   Personal Health Analytics Engine"
echo "======================================="
echo ""

read -p "Create Metriq LXC container now? (y/n): " choice

if [[ "$choice" != "y" ]]; then
  echo "Installation cancelled."
  exit
fi

echo ""
echo "Configuring container..."

CTID=210
HOSTNAME="metriq"
TEMPLATE=$(pveam available | grep debian-12-standard | awk '{print $2}' | tail -n1)
STORAGE="local-lvm"

echo "Updating template list..."
pveam update

if ! pveam list local | grep -q "$TEMPLATE"; then
  echo "Downloading Debian 12 template..."
  pveam download local $TEMPLATE
fi

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

echo ""
echo "Waiting for networking..."
sleep 15

echo ""
echo "Installing Metriq..."

pct exec $CTID -- bash -c "
apt update
apt install -y curl
curl -sSL https://raw.githubusercontent.com/dahellmonster/metriq/main/install.sh | bash
"

echo ""
echo "======================================="
echo " Metriq Installed Successfully"
echo "======================================="
echo ""

echo "Check container IP with:"
echo "pct exec $CTID -- ip a"

echo ""
echo "Then open:"
echo "http://CONTAINER_IP:8000/analytics"