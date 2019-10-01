#!/bin/bash
# Default variables
folder="/tmp/pwnagotchi"
version="master"
commit=0
backupconfig=0
restoreconfig=0

# functions
function display_help {
        echo "Usage: $0 [-m | --master] [-c | --commit | --branch] [-bc | --backupconfig] [-rc | --restoreconfig] [-h | --help]" >&2
        echo
        echo "   -m, --master               Update to the master branch. Used by default."
        echo "   -c, --commit, --branch     Update to the specific commit/branch."
        echo "   -bc, --backupconfig        Backup the current pwnagotchi config."
        echo "   -rc, --restoreconfig       Restore the current pwnagotchi config. -bc will be enabled."
        echo "   -h, --help                 Shows this help."
        echo ""
        echo
        exit 1
}
function test_root {
# Check if we are running as root.
    if ! [ $(id -u) = 0 ]; then
            echo " [!] This script must be run as root."
            exit 3
    fi
}
function test_github {
    wget -q  --spider https://github.com/evilsocket/pwnagotchi/
    if [ $? -ne 0 ]; then
            echo " [!] Cannot reach github. This script requires internet access, ensure connection sharing is working."
            exit 4
    fi
}

# Commandline arguments
while [[ "$#" -gt 0 ]]; do case $1 in
        -m|--master) version="master"; shift;;
        -c|--commit|---branch) commit="$2" version="other"; shift;;
        -bc|--backupconfig) backupconfig=1; shift;;
        -rc|--restoreconfig) backupconfig=1 restoreconfig=1; shift;;
        -h|--help) display_help;;
        *) echo "Unknown parameter passed: $1"; exit 2;;
esac; shift; done

echo " [+] Checking prerequisites."
test_root
test_github

# clean up old files, clone master, set checkout to commit if needed.
echo " [+] Cloning to $folder..."
rm $folder -rf
git clone https://github.com/evilsocket/pwnagotchi $folder -q
cd $folder
if [ $version == "other" ]; then
        git checkout $commit -q
fi
echo " [+] Installing $(git log -1 --format="%h")"

echo " [+] Updating..."
if [ $backupconfig -eq 1 ]; then
        echo " [+] Creating backup of config.yml"
        mv /root/pwnagotchi/config.yml ~/config.yml.bak -f
fi
rm /root/pwnagotchi -rf
rsync -aPq $folder/sdcard/rootfs/* /
cd /tmp
rm $folder -rf
if [ $restoreconfig -eq 1 ]; then
        echo " [+] Restoring backup of config.yml"
        mv ~/config.yml.bak /root/pwnagotchi/config.yml -f
fi

echo " [+] Restarting pwnagotchi in auto mode. $( screen -X -S pwnagotchi quit)"
sudo -H -u root /usr/bin/screen -dmS pwnagotchi -c /root/pwnagotchi/data/screenrc.auto
echo " [+] Finished"