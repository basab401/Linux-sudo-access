#!/bin/bash -
#title           :create_systemd_service.sh
#description     :This script will install the application as a systemd service
#author          :basabjit
#date            :2019-Mar-30
#version         :0.1
#usage           :bash  create_systemd_service.sh

SYSTEMD_SCRIPT_DIR=$( cd  $(dirname "${BASH_SOURCE:=$0}") && pwd)
cp -f "$SYSTEMD_SCRIPT_DIR/../systemd/sudo-access.service" /lib/systemd/system
chown root:root /lib/systemd/system/sudo-access.service

systemctl daemon-reload
systemctl start  sudo-access.service
systemctl enable sudo-access.service
