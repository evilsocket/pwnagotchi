#!/bin/sh

usage() {
	echo "Usage: restore.sh [-bhnu] [-h] [-b backup name] [-n host name] [-u user name]"
}

while getopts "hb:n:u:" arg; do
	case $arg in
		b)
			BACKUP=$OPTARG
			;;
		h)
			usage
			exit
			;;
		n)
			UNIT_HOSTNAME=$OPTARG
			;;
		u)
			UNIT_USERNAME=$OPTARG
			;;
		*)
			usage
			exit 1
	esac
done
# name of the ethernet gadget interface on the host
UNIT_HOSTNAME=${UNIT_HOSTNAME:-10.0.0.2}
# output backup tgz file
if [ -z $BACKUP ]; then
	BACKUP=$(ls -rt ${UNIT_HOSTNAME}-backup-*.tgz 2>/dev/null | tail -n1)
	if [ -z $BACKUP ]; then
		echo "@ Can't find backup file. Please specify one with '-b'"
		exit 1
	fi
	echo "@ Found backup file:"
	echo "\t${BACKUP}"
	echo -n "@ continue restroring this file? (y/n) "
	read CONTINUE
	CONTINUE=$(echo "${CONTINUE}" | tr "[:upper:]" "[:lower:]")
	if [ "${CONTINUE}" != "y" ]; then
		exit 1
	fi
fi
# username to use for ssh
UNIT_USERNAME=${UNIT_USERNAME:-pi}

ping -c 1 "${UNIT_HOSTNAME}" > /dev/null 2>&1 || {
  echo "@ unit ${UNIT_HOSTNAME} can't be reached, make sure it's connected and a static IP assigned to the USB interface."
  exit 1
}

echo "@ restoring $BACKUP to $UNIT_HOSTNAME ..."
cat ${BACKUP} | ssh "${UNIT_USERNAME}@${UNIT_HOSTNAME}" "sudo tar xzv -C /"
