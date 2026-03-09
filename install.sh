#!/bin/bash
set -e

apt update
apt install -y python3 python3-venv python3-pip git

cd /opt

if [ ! -d metriq ]; then
  git clone https://github.com/dahellmonster/metriq.git
fi

cd metriq

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp systemd.service /etc/systemd/system/metriq.service

systemctl daemon-reload
systemctl enable metriq
systemctl restart metriq
