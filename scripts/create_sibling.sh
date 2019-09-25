#!/bin/bash
# based on: https://wiki.debian.org/RaspberryPi/qemu-user-static
## and https://z4ziggy.wordpress.com/2015/05/04/from-bochs-to-chroot/

set -eu

REQUIREMENTS=( wget gunzip git dd e2fsck resize2fs parted losetup qemu-system-x86_64 )
REPO_DIR="$(dirname "$(dirname "$(realpath "$0")")")"
TMP_DIR="${REPO_DIR}/tmp"
MNT_DIR="${TMP_DIR}/mnt"

PWNI_NAME="pwnagotchi"
PWNI_OUTPUT="pwnagotchi.img"
PWNI_SIZE="4"

OPT_PROVISION_ONLY=0
OPT_CHECK_DEPS_ONLY=0

if [[ "$EUID" -ne 0 ]]; then
   echo "Run this script as root!"
   exit 1
fi

function check_dependencies() {
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
  echo "[+] Downloading raspbian.zip"
  mkdir -p "${TMP_DIR}"
  wget --show-progress -qcO "${TMP_DIR}/raspbian.zip" "https://downloads.raspberrypi.org/raspbian_lite_latest"
  echo "[+] Unpacking raspbian.zip to raspbian.img"
  gunzip -c "${TMP_DIR}/raspbian.zip" > "${TMP_DIR}/raspbian.img"
}

function setup_raspbian(){
  echo "[+] Resize image"
  dd if=/dev/zero bs=1G count="$PWNI_SIZE" >> "${TMP_DIR}/raspbian.img"
  echo "[+] Setup loop device"
  mkdir -p "${MNT_DIR}"
  LOOP_PATH="$(losetup --find --partscan --show "${TMP_DIR}/raspbian.img")"
  PART2_START="$(parted -s "$LOOP_PATH" -- print | awk '$1==2{ print $2 }')"
  parted -s "$LOOP_PATH" rm 2
  parted -s "$LOOP_PATH" mkpart primary "$PART2_START" 100%
  echo "[+] Check FS"
  e2fsck -f "${LOOP_PATH}p2"
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
  mount --bind /etc/ssl/certs "${MNT_DIR}/etc/ssl/certs"
  mount --bind /etc/ca-certificates "${MNT_DIR}/etc/ca-certificates"
  cp /usr/bin/qemu-arm-static "${MNT_DIR}/usr/bin"
}

function provision_raspbian() {
  cd "${MNT_DIR}"
  sed -i'' 's/^\([^#]\)/#\1/g' etc/ld.so.preload # add comments
  echo "[+] Run chroot commands"
  LANG=C chroot . bin/bash -x <<EOF
  set -eu
  export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
  apt-get -y update
  apt-get -y upgrade
  apt-get -y install git vim screen build-essential golang python3-pip
  apt-get -y install libpcap-dev libusb-1.0-0-dev libnetfilter-queue-dev
  apt-get -y install dphys-swapfile libopenmpi-dev libatlas-base-dev
  apt-get -y install libjasper-dev libqtgui4 libqt4-test

  # setup dphys-swapfile
  echo "CONF_SWAPSIZE=1024" >/etc/dphys-swapfile
  systemctl enable dphys-swapfile.service

  # install pwnagotchi
  cd /tmp
  git clone https://github.com/evilsocket/pwnagotchi.git
  rsync -aP pwnagotchi/sdcard/boot/* /boot/
  rsync -aP pwnagotchi/sdcard/rootfs/* /

  # configure pwnagotchi
  echo -e "$PWNI_NAME" > /etc/hostname
  sed -i "s@^127\.0\.0\.1 .*@127.0.0.1 localhost "$PWNI_NAME" "$PWNI_NAME".local@g" /etc/hosts
  sed -i "s@pwnagotchi@$PWNI_NAME@g" /etc/motd

  chmod +x /etc/rc.local

  </root/pwnagotchi/scripts/requirements.txt xargs -I{} --max-args=1 --max-procs="$(nproc)"\
    pip3 install --trusted-host www.piwheels.org {} >/dev/null 2>&1

  # waveshare
  pip3 install --trusted-host www.piwheels.org spidev RPi.GPIO

  # install bettercap
  export GOPATH=/root/go
  go get -u github.com/bettercap/bettercap
  mv "\$GOPATH/bin/bettercap" /usr/bin/bettercap

  # install bettercap caplets (cant run bettercap in chroot)
  cd /tmp
  git clone https://github.com/bettercap/caplets.git
  cd caplets
  make install

  # monstart + monstop
  cat <<"STOP" > /usr/bin/monstop
  #!/bin/bash
  interface=mon0
  ifconfig \${interface} down
  sleep 1
  iw dev \${interface} del
STOP

  cat <<"STOP" > /usr/bin/monstart
  interface=mon0
  echo "Bring up monitor mode interface \${interface}"
  iw phy phy0 interface add \${interface} type monitor
  ifconfig \${interface} up
  if [ \$? -eq 0 ]; then
      echo "started monitor interface on \${interface}"
  fi
STOP

  chmod +x /usr/bin/{monstart,monstop}

  # Re4son-Kernel
  echo "deb http://http.re4son-kernel.com/re4son/ kali-pi main" > /etc/apt/sources.list.d/re4son.list
  wget -O - https://re4son-kernel.com/keys/http/archive-key.asc | apt-key add -
  apt update
  apt install -y kalipi-kernel kalipi-bootloader kalipi-re4son-firmware kalipi-kernel-headers libraspberrypi0 libraspberrypi-dev libraspberrypi-doc libraspberrypi-bin
EOF
  sed -i'' 's/^#//g' etc/ld.so.preload
  cd "${REPO_DIR}"
  umount -R "${MNT_DIR}"
  losetup -D "$(losetup -l | awk '/raspbian\.img/{print $1}')"
  mv "${TMP_DIR}/raspbian.img" "$PWNI_OUTPUT"
}

function usage() {
  cat <<EOF

usage: $0 [OPTIONS]

  Options:
    -n <name> # Name of the pwnagotchi (default: pwnagotchi)
    -o <file> # Name of the img-file (default: pwnagotchi.img)
    -s <size> # Size which should be added to second partition (in Gigabyte) (default: 4)
    -p        # Only run provisioning (assumes the image is already mounted)
    -d        # Only run dependencies checks
    -h        # Show this help

EOF

  exit 0
}

while getopts ":n:o:s:dph" o; do
  case "${o}" in
    n)
      PWNI_NAME="${OPTARG}"
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
get_raspbian
setup_raspbian
provision_raspbian

echo -ne "[+] Congratz, it's a boy (⌐■_■)!\n[+] One more step: dd if=$PWNI_OUTPUT of=<PATH_TO_SDCARD> bs=4M status=progress"
