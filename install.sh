#!/bin/bash
set -e

echo "Updating system packages..."
apt update
apt install -y python3 python3-venv python3-pip git build-essential

echo "Installing Metriq..."

cd /opt

# clone repo if it doesn't exist
if [ ! -d "metriq" ]; then
  git clone https://github.com/dahellmonster/metriq.git
fi

cd metriq

echo "Creating Python virtual environment..."

python3 -m venv venv

source venv/bin/activate

echo "Upgrading pip..."

pip install --upgrade pip

echo "Installing Python dependencies..."

pip install -r requirements.txt

echo "Installing systemd service..."

cp systemd.service /etc/systemd/system/metriq.service

systemctl daemon-reload
systemctl enable metriq

echo "Starting Metriq service..."

systemctl restart metriq

echo "Metriq installation complete."