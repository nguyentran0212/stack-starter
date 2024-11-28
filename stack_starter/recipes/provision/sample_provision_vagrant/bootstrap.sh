#!/usr/bin/env bash

apt-get update
apt-get install -y avahi-daemon avahi-utils libnss-mdns

# Get the current hostname
HOSTNAME=$(hostname)

# Configure Avahi with the hostname
sed -i "s/#host-name=.*/host-name=$HOSTNAME/" /etc/avahi/avahi-daemon.conf

# Restart Avahi daemon to apply changes
systemctl restart avahi-daemon

