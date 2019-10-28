#!/usr/bin/env bash

# name of the ethernet gadget interface on the host
UNIT_HOSTNAME=${1:-10.0.0.2}
# output backup zip file
OUTPUT=${2:-pwnagotchi-backup.zip}
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
  /home/pi/.bashrc
  /etc/network/interfaces.d/usb0-cfg
  /etc/hostname
  /etc/hosts

  
)

ping -c 1 "${UNIT_HOSTNAME}" >/dev/null || {
  echo "@ unit ${UNIT_HOSTNAME} can't be reached, make sure it's connected and a static IP assigned to the USB interface."
  exit 1
}

echo "@ backing up $UNIT_HOSTNAME to $OUTPUT ..."

ssh "${USERNAME}@${UNIT_HOSTNAME}" "sudo rm -rf /tmp/backup && sudo rm -rf /tmp/backup.zip" > /dev/null

for file in "${FILES_TO_BACKUP[@]}"; do
  dir=$(dirname "$file")

  echo "@ copying $file to /tmp/backup$dir"

  ssh "${USERNAME}@${UNIT_HOSTNAME}" "mkdir -p /tmp/backup${dir}" > /dev/null
  ssh "${USERNAME}@${UNIT_HOSTNAME}" "sudo cp -r ${file} /tmp/backup${dir}" > /dev/null
done

ssh "${USERNAME}@${UNIT_HOSTNAME}" "sudo chown ${USERNAME}:${USERNAME} -R /tmp/backup" > /dev/null

echo "@ pulling from $UNIT_HOSTNAME ..."

rm -rf /tmp/backup
scp -rC "${USERNAME}@${UNIT_HOSTNAME}":/tmp/backup /tmp/

echo "@ compressing ..."

zip -r -9 -q "$OUTPUT" /tmp/backup
rm -rf /tmp/backup

