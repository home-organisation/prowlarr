#!/usr/bin/with-contenv bash
# shellcheck shell=bash

python /app/init/init.py

# bug MEDIACORE-670
sleep 5
ip=$(nslookup -type=A www.yggtorrent.top 192.168.1.21 | grep Address | awk '{ print $2 }' | sed -n 2p)
echo "Adding www.yggtorrent.top to /etc/hosts with IP ${ip}"
echo "${ip}    www.yggtorrent.top" >> /etc/hosts