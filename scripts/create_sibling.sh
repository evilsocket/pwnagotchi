#!/usr/bin/env bash
# based on: https://wiki.debian.org/RaspberryPi/qemu-user-static
## and https://z4ziggy.wordpress.com/2015/05/04/from-bochs-to-chroot/

set -eu

REQUIREMENTS=( wget gunzip git dd e2fsck resize2fs parted losetup qemu-system-x86_64 )
DEBREQUIREMENTS=( wget gzip git parted qemu-system-x86 qemu-user-static )
REPO_DIR="$(dirname "$(dirname "$(realpath "$0")")")"
TMP_DIR="${REPO_DIR}/tmp"
MNT_DIR="${TMP_DIR}/mnt"
THIS_DIR=$(pwd)

PWNI_NAME="pwnagotchi"
PWNI_OUTPUT="pwnagotchi.img"
PWNI_SIZE="8"

OPT_SPARSE=0
OPT_PROVISION_ONLY=0
OPT_CHECK_DEPS_ONLY=0
OPT_IMAGE_PROVIDED=0
OPT_RASPBIAN_VERSION='latest'
OPT_APTPROXY=""

SUPPORTED_RASPBIAN_VERSIONS=( 'latest' 'buster' 'stretch' )

if [[ "$EUID" -ne 0 ]]; then
   echo "Run this script as root!"
   exit 1
fi

function check_dependencies() {
  if [ -f /etc/debian_version ];
  then
    echo "[+] Checking Debian dependencies"

    for REQ in "${DEBREQUIREMENTS[@]}"; do
      if ! dpkg -s "$REQ" >/dev/null 2>&1; then
        echo "Dependency check failed for ${REQ}; use 'apt-get install ${REQ}' to install"
        exit 1
      fi
    done
  fi

  echo "[+] Checking dependencies"
  for REQ in "${REQUIREMENTS[@]}"; do
    if ! type "$REQ" >/dev/null 2>&1; then
      echo "Dependency check failed for ${REQ}"
      exit 1
    fi
  done

  if ! test -e /usr/bin/qemu-arm-static; then
    echo "[-] You need the package \"qemu-user-static\" for this to work."
    exit 1
  fi

  if ! systemctl is-active systemd-binfmt.service >/dev/null 2>&1; then
     mkdir -p "/lib/binfmt.d"
     echo ':qemu-arm:M::\x7fELF\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x28\x00:\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe\xff\xff\xff:/usr/bin/qemu-arm-static:F' > /lib/binfmt.d/qemu-arm-static.conf
     systemctl restart systemd-binfmt.service
  fi
}

function get_raspbian() {
  VERSION="$1"

  case "$VERSION" in
    latest)
      URL="https://downloads.raspberrypi.org/raspbian_lite_latest"
      ;;
    buster)
      URL="https://downloads.raspberrypi.org/raspbian/images/raspbian-2019-07-12/2019-07-10-raspbian-buster.zip"
      ;;
    stretch)
      URL="https://downloads.raspberrypi.org/raspbian/images/raspbian-2019-04-09/2019-04-08-raspbian-stretch.zip"
      ;;
  esac

  echo "[+] Downloading raspbian.zip"
  mkdir -p "${TMP_DIR}"
  wget --show-progress -qcO "${TMP_DIR}/raspbian.zip" "$URL"
  echo "[+] Unpacking raspbian.zip to raspbian.img"
  gunzip -c "${TMP_DIR}/raspbian.zip" > "${TMP_DIR}/raspbian.img"
}

function provide_raspbian() {
  echo "[+] Providing path of raspbian file"
  mkdir -p "${TMP_DIR}"
  echo "[+] Unpacking raspbian.zip to raspbian.img"
  gunzip -c "${PWNI_INPUT}" > "${TMP_DIR}/raspbian.img"
}

function setup_raspbian(){
  # Detect the ability to create sparse files
  if [ "${OPT_SPARSE}" -eq 0 ]; then
    if ! type "bmaptool" >/dev/null 2>&1; then
      echo "[!] bmaptool not available, not creating a sparse image"
    else
      echo "[+] Defaulting to sparse image generation as bmaptool is available"
      OPT_SPARSE=1
    fi
  fi

  # Note that we 'extend' the raspbian.img
  if [ "${OPT_SPARSE}" -eq 1 ];
  then
    # Resize sparse (so that we can use bmaptool later)
    echo "[+] Resizing sparse image of ${PWNI_SIZE}GB (1000s)"
    truncate -s ${PWNI_SIZE}GB "${TMP_DIR}/raspbian.img"
  else
    echo "[+] Resizing full image to ${PWNI_SIZE}G"
    # Full disk-space using image (appends to raspbian image)
    dd if=/dev/zero bs=1G count="${PWNI_SIZE}" >> "${TMP_DIR}/raspbian.img"
  fi

  echo "[+] Setup loop device"
  mkdir -p "${MNT_DIR}"
  LOOP_PATH="$(losetup --find --partscan --show "${TMP_DIR}/raspbian.img")"
  PART2_START="$(parted -s "$LOOP_PATH" -- print | awk '$1==2{ print $2 }')"
  parted -s "$LOOP_PATH" rm 2
  parted -s "$LOOP_PATH" mkpart primary "$PART2_START" 100%
  echo "[+] Check FS"
  e2fsck -y -f "${LOOP_PATH}p2"
  echo "[+] Resize FS"
  resize2fs "${LOOP_PATH}p2"
  echo "[+] Device is ${LOOP_PATH}"
  echo "[+] Unmount if already mounted with other img"
  mountpoint -q "${MNT_DIR}" && umount -R "${MNT_DIR}"
  echo "[+] Mount /"
  mount -o rw "${LOOP_PATH}p2" "${MNT_DIR}"
  echo "[+] Mount /boot"
  mount -o rw "${LOOP_PATH}p1" "${MNT_DIR}/boot"
  mount --bind /dev "${MNT_DIR}/dev/"
  mount --bind /sys "${MNT_DIR}/sys/"
  mount --bind /proc "${MNT_DIR}/proc/"
  mount --bind /dev/pts "${MNT_DIR}/dev/pts"
  cp /usr/bin/qemu-arm-static "${MNT_DIR}/usr/bin"
  cp /etc/resolv.conf "${MNT_DIR}/etc/resolv.conf"
}

function provision_raspbian() {
  cd "${MNT_DIR}"
  sed -i'' 's/^\([^#]\)/#\1/g' etc/ld.so.preload # add comments
  echo "[+] Run chroot commands"
  LANG=C LC_ALL=C LC_CTYPE=C chroot . bin/bash -x <<EOF
  set -eu
  export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

  if [ ! -z "${OPT_APTPROXY}" ];
  then
	echo "[+] Using Proxy ${OPT_APTPROXY}"
	echo "Acquire::http { Proxy \"${OPT_APTPROXY}\"; }" >/etc/apt/apt.conf.d/99pwnagotchi_proxy
  fi

  uname -a

  apt-get -y update
  apt-get -y upgrade
  apt-get -y install git vim screen build-essential golang python3-pip gawk
  apt-get -y install libpcap-dev libusb-1.0-0-dev libnetfilter-queue-dev
  apt-get -y install dphys-swapfile libopenmpi-dev libatlas-base-dev
  apt-get -y install libjasper-dev libqtgui4 libqt4-test libopenjp2-7
  apt-get -y install tcpdump libilmbase23 libopenexr23 libgstreamer1.0-0
  apt-get -y install libavcodec58 libavformat58 libswscale5

  # setup dphys-swapfile
  echo "CONF_SWAPSIZE=1024" >/etc/dphys-swapfile
  systemctl enable dphys-swapfile.service

  # install pwnagotchi
  cd /tmp
  git clone https://github.com/evilsocket/pwnagotchi.git
  rsync -aP pwnagotchi/sdcard/boot/* /boot/
  rsync -aP pwnagotchi/sdcard/rootfs/* /
  rm -rf /tmp/pwnagotchi

  # configure pwnagotchi
  echo -e "$PWNI_NAME" > /etc/hostname
  sed -i "s@^127\.0\.0\.1 .*@127.0.0.1 localhost "$PWNI_NAME" "$PWNI_NAME".local@g" /etc/hosts
  sed -i "s@alpha@$PWNI_NAME@g" /etc/motd

  chmod +x /etc/rc.local

  # need armv6l version of tensorflow and opencv-python, not armv7l
  # PIP_OPTS="--upgrade --only-binary :all: --abi cp37m --platform linux_armv6l --target /usr/lib/python3.7/site-packages/"
  # pip3 install \$PIP_OPTS opencv-python
  # Should work for tensorflow too, but BUG: Hash mismatch; therefore:
  wget -P /root/ -c https://www.piwheels.org/simple/tensorflow/tensorflow-1.13.1-cp37-none-linux_armv6l.whl
  wget -P /root/ -c https://www.piwheels.org/simple/opencv-python/opencv_python-3.4.3.18-cp37-cp37m-linux_armv6l.whl
  # we need to install these on first raspberry start...
  sed -i '/startup\.sh/i pip3 install --no-deps --force-reinstall --upgrade /root/tensorflow-1.13.1-cp37-none-linux_armv6l.whl /root/opencv_python-3.4.3.18-cp37-cp37m-linux_armv6l.whl && rm /root/tensorflow-1.13.1-cp37-none-linux_armv6l.whl /root/opencv_python-3.4.3.18-cp37-cp37m-linux_armv6l.whl && sed -i "/tensorflow/d" /etc/rc.local' /etc/rc.local

  # newer version is broken
  pip3 install gast==0.2.2

  </root/pwnagotchi/scripts/requirements.txt xargs -I{} --max-args=1 --max-procs="$(nproc)"\
    pip3 install --progress-bar off {}

  # waveshare
  pip3 install spidev RPi.GPIO

  # install bettercap
  export GOPATH=/root/go
  taskset -c 1 go get -u github.com/bettercap/bettercap
  mv "\$GOPATH/bin/bettercap" /usr/bin/bettercap

  # install bettercap caplets (cant run bettercap in chroot)
  cd /tmp
  git clone https://github.com/bettercap/caplets.git
  cd caplets
  make install
  rm -rf /tmp/caplets
  cd /root # fixes getcwd error that was bugging me

  # Re4son-Kernel
  echo "deb http://http.re4son-kernel.com/re4son/ kali-pi main" > /etc/apt/sources.list.d/re4son.list
  wget -O - https://re4son-kernel.com/keys/http/archive-key.asc | apt-key add -
  apt update
  apt install -y kalipi-kernel kalipi-bootloader kalipi-re4son-firmware kalipi-kernel-headers libraspberrypi0 libraspberrypi-dev libraspberrypi-doc libraspberrypi-bin

  # Fix PARTUUID
  PUUID_ROOT="\$(blkid "\$(df / --output=source | tail -1)" | grep -Po 'PARTUUID="\K[^"]+')"
  PUUID_BOOT="\$(blkid "\$(df /boot --output=source | tail -1)" | grep -Po 'PARTUUID="\K[^"]+')"

  # sed regex info: search for line containing / followed by whitespace or /boot (second sed)
  #                 in this line, search for PARTUUID= followed by letters, numbers or "-"
  #                 replace that match with the new PARTUUID
  sed -i "/\/[ ]\+/s/PARTUUID=[A-Za-z0-9-]\+/PARTUUID=\$PUUID_ROOT/g" /etc/fstab
  sed -i "/\/boot/s/PARTUUID=[A-Za-z0-9-]\+/PARTUUID=\$PUUID_BOOT/g" /etc/fstab

  sed -i "s/root=[^ ]\+/root=PARTUUID=\${PUUID_ROOT}/g" /boot/cmdline.txt

  # delete keys
  find /etc/ssh/ -name "ssh_host_*key*" -delete

  # slows down boot
  systemctl disable apt-daily.timer apt-daily.service apt-daily-upgrade.timer apt-daily-upgrade.service

  # unecessary services
  systemctl disable triggerhappy bluetooth wpa_supplicant

EOF
  sed -i'' 's/^#//g' etc/ld.so.preload
  cd "${REPO_DIR}"
  umount -R "${MNT_DIR}"
  losetup -D "$(losetup -l | awk '/raspbian\.img/{print $1}')"
  mv "${TMP_DIR}/raspbian.img" "${PWNI_OUTPUT}"
  if [ "${OPT_SPARSE}" -eq 1 ];
  then
    bmaptool create -o "${PWNI_OUTPUT}.bmap" "${PWNI_OUTPUT}"
  fi
}

function usage() {
  cat <<EOF

usage: $0 [OPTIONS]

  Options:
    -n <name>    # Name of the pwnagotchi (default: pwnagotchi)
    -i <file>    # Provide the path of an already downloaded raspbian image
    -o <file>    # Name of the img-file (default: pwnagotchi.img)
    -s <size>    # Size which should be added to second partition (in Gigabyte) (default: 4)
    -v <version> # Version of raspbian (Supported: ${SUPPORTED_RASPBIAN_VERSIONS[*]}; default: latest)
    -p           # Only run provisioning (assumes the image is already mounted)
    -d           # Only run dependencies checks
    -h           # Show this help

EOF

  exit 0
}

while getopts "A:n:i:o:s:v:dph" o; do
  case "${o}" in
    A)
      OPT_APTPROXY="${OPTARG}"
      ;;
    n)
      PWNI_NAME="${OPTARG}"
      ;;
    i)
      PWNI_INPUT="${OPTARG}"
      OPT_IMAGE_PROVIDED=1
      ;;
    o)
      PWNI_OUTPUT="${OPTARG}"
      ;;
    s)
      PWNI_SIZE="${OPTARG}"
      ;;
    p)
      OPT_PROVISION_ONLY=1
      ;;
    d)
      OPT_CHECK_DEPS_ONLY=1
      ;;
    v)
      if [[ "${SUPPORTED_RASPBIAN_VERSIONS[*]}" =~ ${OPTARG} ]]; then
        OPT_RASPBIAN_VERSION="${OPTARG}"
      else
        usage
      fi
      ;;
    h)
      usage
      ;;
    *)
      usage
      ;;
  esac
done
shift $((OPTIND-1))

if [[ "$OPT_PROVISION_ONLY" -eq 1 ]]; then
  provision_raspbian
  exit 0
elif [[ "$OPT_CHECK_DEPS_ONLY" -eq 1 ]]; then
  check_dependencies
  exit 0
fi

check_dependencies

if [[ "$OPT_IMAGE_PROVIDED" -eq 1 ]]; then
  provide_raspbian
else
  get_raspbian "$OPT_RASPBIAN_VERSION"
fi

setup_raspbian
provision_raspbian

#Make a baby with a random gender, maybe do something fun with this later!
gender[0]="boy"
gender[1]="girl"

rand=$[ $RANDOM % 2 ]

echo -e "[+] Congratz, it's a ${gender[$rand]} (⌐■_■)!"
echo -e "[+] One more step: dd if=../${PWNI_OUTPUT} of=<PATH_TO_SDCARD> bs=4M status=progress"

if [ "${OPT_SPARSE}" -eq 1 ];
then
  echo -e "[t] To transfer use: rsync -vaS --progress $(whoami)@$(hostname -f):${THIS_DIR}/../${PWNI_OUTPUT} <DEST>"
  echo -e "[t] To burn with bmaptool: bmaptool copy ~/${PWNI_OUTPUT} /dev/<DEVICE>"
fi

# Helpful OSX reminder
echo -e "[t] Mac: use 'diskutil list' to figure out which device to burn to; 'diskutil unmountDisk' to unmount that disk'; then use /dev/rdiskX (note the 'r') for faster transfer"
