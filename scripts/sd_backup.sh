#!/bin/sh

usage() {
	echo "Usage: sd_backup.sh [-hod] [-h] [-d rootfs dir] [-o output]"
}

while getopts "ho:d:u:" arg; do
	case $arg in
		h)
			usage
			exit
			;;
		d)
			SD_DIR=$OPTARG
			;;
		o)
			OUTPUT=$OPTARG
			;;
		*)
			usage
			exit 1
	esac
done

sudo xargs -a dirs.list -L 1 -I @ find ${SD_DIR%/}@ -type f -print0 | xargs -0 sudo tar cv | gzip -9 > "$OUTPUT"
