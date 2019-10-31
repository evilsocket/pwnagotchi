#!/usr/bin/env bash

# name of the ethernet gadget interface on the host
UNIT_HOSTNAME=${1:-10.0.0.2}
# output backup zip file
BACKUP=${2:-pwnagotchi-backup.tgz}
# username to use for ssh
USERNAME=${3:-pi}

ping -c 1 "${UNIT_HOSTNAME}" >/dev/null || {
  echo "@ unit ${UNIT_HOSTNAME} can't be reached, make sure it's connected and a static IP assigned to the USB interface."
  exit 1
}

echo "@ restoring $BACKUP to $UNIT_HOSTNAME ..."
cat ${BACKUP} | ssh "${USERNAME}@${UNIT_HOSTNAME}" "sudo tar xzv -C /"
