#!/bin/bash
# Default variables
git_folder="/tmp/pwnagotchi"
git_url="https://github.com/evilsocket/pwnagotchi/"
version="master"
backupconfig=0
restoreconfig=0

# Functions
function usage() {
        cat <<EOF

 usage: $0 [OPTIONS]

   Options:
      -v, --version              # Version to update to, can be a branch or commit. (default: master)
      -u, --url                  # Url to clone from. (default: https://github.com/evilsocket/pwnagotchi)
      -bc, --backupconfig        # Backup the current pwnagotchi config.
      -rc, --restoreconfig       # Restore the current pwnagotchi config. -bc will be enabled.
      -h, --help                 # Shows this help.

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
    wget -q  --spider $git_url
    if [ $? -ne 0 ]; then
            echo "[!] Cannot reach github. This script requires internet access, ensure connection sharing is working."
            exit 2
    fi
}

# Commandline arguments
while [[ "$#" -gt 0 ]]; do case $1 in
        -v|--version) version="$2"; shift;;
        -u|--url) git_url="$2"; shift;;
        -bc|--backupconfig) backupconfig=1; shift;;
        -rc|--restoreconfig) backupconfig=1 restoreconfig=1; shift;;
        -h|--help) usage;;
        *) echo "Unknown parameter passed: $1"; exit 3;;
esac; shift; done

echo "[+] Checking prerequisites."
test_root
test_github

# clean up old files, clone master, set checkout to commit if needed.
echo "[+] Cloning to $git_folder..."
rm $git_folder -rf
git clone $git_url $git_folder -q
cd $git_folder
if [ $version != "master" ]; then
        git checkout $version -q
fi
echo "[+] Installing $(git log -1 --format="%h")"

echo "[+] Updating..."
if [ $backupconfig -eq 1 ]; then
        echo "[+] Creating backup of config.yml"
        mv /root/pwnagotchi/config.yml /root/config.yml.bak -f
fi
rm /root/pwnagotchi -rf # ensures old files are removed
rsync -aPq $git_folder/sdcard/boot/*   /boot/
rsync -aPq $git_folder/sdcard/rootfs/* /
cd /tmp
rm $git_folder -rf
if [ $restoreconfig -eq 1 ]; then
        echo "[+] Restoring backup of config.yml"
        mv /root/config.yml.bak /root/pwnagotchi/config.yml -f
fi

echo "[+] Restarting pwnagotchi in auto mode. $( screen -X -S pwnagotchi quit)"
sudo -H -u root /usr/bin/screen -dmS pwnagotchi -c /root/pwnagotchi/data/screenrc.auto
echo "[+] Finished"