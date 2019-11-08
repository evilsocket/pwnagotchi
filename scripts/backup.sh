#!/usr/bin/env bash

# name of the ethernet gadget interface on the host
UNIT_HOSTNAME=${1:-10.0.0.2}
# output backup zip file
OUTPUT=${2:-pwnagotchi-backup.tgz}
# username to use for ssh
USERNAME=${3:-pi}
# what to backup
FILES_TO_BACKUP=(
  /root/brain.nn
  /root/brain.json
  /root/.api-report.json
  /root/.bashrc
  /root/handshakes
  /root/peers
  /etc/pwnagotchi/
  /var/log/pwnagotchi.log
  /var/log/pwnagotchi*.gz
  /home/pi/.bashrc
)

ping -c 1 "${UNIT_HOSTNAME}" >/dev/null || {
  echo "@ unit ${UNIT_HOSTNAME} can't be reached, make sure it's connected and a static IP assigned to the USB interface."
  exit 1
}

echo "@ backing up $UNIT_HOSTNAME to $OUTPUT ..."
ssh "${USERNAME}@${UNIT_HOSTNAME}" "sudo tar cv ${FILES_TO_BACKUP[@]}" | gzip -9 > "$OUTPUT"
