#!/usr/bin/env bash

# name of the ethernet gadget interface on the host
UNIT_HOSTNAME=${1:-10.0.0.2}
# output backup zip file
OUTPUT=${2:-pwnagotchi-backup.zip}
# temporary folder
TEMP_BACKUP_FOLDER=/tmp/pwnagotchi_backup
# what to backup
FILES_TO_BACKUP=(
  /root/brain.nn
  /root/brain.json
  /root/custom.yaml
  /root/handshakes
  /etc/ssh
  /etc/hostname
  /etc/hosts
  /etc/motd
  /var/log/pwnagotchi.log
)

ping -c 1 $UNIT_HOSTNAME >/dev/null || {
  echo "@ unit $UNIT_HOSTNAME can't be reached, make sure it's connected and a static IP assigned to the USB interface."
  exit 1
}

echo "@ backing up $UNIT_HOSTNAME to $OUTPUT ..."

rm -rf "$TEMP_BACKUP_FOLDER"

for file in "${FILES_TO_BACKUP[@]}"; do
  dir=$(dirname $file)
  echo "  $file -> $TEMP_BACKUP_FOLDER$dir/"
  mkdir -p "$TEMP_BACKUP_FOLDER/$dir"
  scp -Cr root@$UNIT_HOSTNAME:$file "$TEMP_BACKUP_FOLDER$dir/"
done

ZIPFILE="$PWD/$OUTPUT"
pushd $PWD
cd "$TEMP_BACKUP_FOLDER"
zip -r -9 -q "$ZIPFILE" .
popd
