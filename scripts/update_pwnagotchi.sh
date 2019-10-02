#!/bin/bash
# Default variables
GIT_FOLDER="/tmp/pwnagotchi"
GIT_URL="https://github.com/evilsocket/pwnagotchi/"
VERSION="master"
SUPPORTED_RESTART_MODES=( 'auto' 'manual' )
MODE="auto"
BACKUPCONFIG=0
RESTORECONFIG=0

# Functions
function usage() {
    cat <<EOF

 usage: $0 [OPTIONS]
 
   Options:
      -v        # Version to update to, can be a branch or commit. (default: master)
      -u        # Url to clone from. (default: https://github.com/evilsocket/pwnagotchi)
      -m        # Mode to restart to. (Supported: ${SUPPORTED_RESTART_MODES[*]}; default: auto)
      -b        # Backup the current pwnagotchi config.
      -r        # Restore the current pwnagotchi config. (-b will be enabled.)
      -h        # Shows this help.

EOF
    exit 0
}

function test_root() {
    if ! [ $(id -u) = 0 ]; then
        echo "[!] This script must be run as root."
        exit 1
    fi
}

function test_github() {
    wget -q  --spider $GIT_URL
    if [ $? -ne 0 ]; then
        echo "[!] Cannot reach github. This script requires internet access, ensure connection sharing is working."
        exit 2
    fi
}

echo "[+] Checking prerequisites."
test_root
test_github

while getopts ":v:u:m:b:r:h" o; do
  case "${o}" in
    v)
      VERSION="${OPTARG}"
      ;;
    u)
      GIT_URL="${OPTARG}"
      ;;
    m)
      if [[ "${SUPPORTED_RESTART_MODES[*]}" =~ ${OPTARG} ]]; then
        MODE="${OPTARG}"
      else
        usage
      fi      
      ;;      
    b)
      BACKUPCONFIG=1
      ;;
    r)
      BACKUPCONFIG=1    
      RESTORECONFIG=1
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

# clean up old files, clone master, set checkout to commit if needed.
echo "[+] Cloning to $GIT_FOLDER..."
rm $GIT_FOLDER -rf
git clone $GIT_URL $GIT_FOLDER -q
cd $GIT_FOLDER
if [ $VERSION != "master" ]; then
    git checkout $VERSION -q
fi
echo "[+] Installing $(git log -1 --format="%h")"

echo "[+] Updating..."
if [ $BACKUPCONFIG -eq 1 ]; then
    echo "[+] Creating backup of config.yml"
    mv /root/pwnagotchi/config.yml /root/config.yml.bak -f
fi
rm /root/pwnagotchi -rf # ensures old files are removed
rsync -aPq $GIT_FOLDER/sdcard/boot/*   /boot/
rsync -aPq $GIT_FOLDER/sdcard/rootfs/* /
cd /tmp
rm $GIT_FOLDER -rf
if [ $RESTORECONFIG -eq 1 ]; then
    echo "[+] Restoring backup of config.yml"
    mv /root/config.yml.bak /root/pwnagotchi/config.yml -f
fi

echo "[+] Restarting pwnagotchi in $MODE mode. $( screen -X -S pwnagotchi quit)"
if [ $MODE == "auto" ]; then
    sudo -H -u root /usr/bin/screen -dmS pwnagotchi -c /root/pwnagotchi/data/screenrc.auto
elif [ $MODE == "manual" ]; then
    sudo -H -u root /usr/bin/screen -dmS pwnagotchi -c /root/pwnagotchi/data/screenrc.manual
fi
echo "[+] Finished"