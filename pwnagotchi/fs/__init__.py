import os
import re
import tempfile
import contextlib
import shutil
import _thread
import logging

from time import sleep
from distutils.dir_util import copy_tree

mounts = list()


@contextlib.contextmanager
def ensure_write(filename, mode='w'):
    path = os.path.dirname(filename)
    fd, tmp = tempfile.mkstemp(dir=path)

    with os.fdopen(fd, mode) as f:
        yield f
        f.flush()
        os.fsync(f.fileno())

    os.replace(tmp, filename)


def size_of(path):
    """
    Calculate the sum of all the files in path
    """
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    return total


def is_mountpoint(path):
    """
    Checks if path is mountpoint
    """
    return os.system(f"mountpoint -q {path}") == 0


def setup_mounts(config):
    """
    Sets up all the configured mountpoints
    """
    global mounts
    fs_cfg = config['fs']['memory']
    if not fs_cfg['enabled']:
        return

    for name, options in fs_cfg['mounts'].items():
        if not options['enabled']:
            continue
        logging.debug("[FS] Trying to setup mount %s (%s)", name, options['mount'])
        size,unit = re.match(r"(\d+)([a-zA-Z]+)", options['size']).groups()
        target = os.path.join('/run/pwnagotchi/disk/', os.path.basename(options['mount']))

        is_mounted = is_mountpoint(target)
        logging.debug("[FS] %s is %s mounted", options['mount'],
                      "already" if is_mounted else "not yet")

        m = MemoryFS(
            options['mount'],
            target,
            size=options['size'],
            zram=options['zram'],
            zram_disk_size=f"{int(size)*2}{unit}",
            rsync=options['rsync'])

        if not is_mounted:
            if not m.mount():
                logging.debug(f"Error while mounting {m.mountpoint}")
                continue

            if not m.sync(to_ram=True):
                logging.debug(f"Error while syncing to {m.mountpoint}")
                m.umount()
                continue

        interval = int(options['sync'])
        if interval:
            logging.debug("[FS] Starting thread to sync %s (interval: %d)",
                        options['mount'], interval)
            _thread.start_new_thread(m.daemonize, (interval,))
        else:
            logging.debug("[FS] Not syncing %s, because interval is 0",
            options['mount'])

        mounts.append(m)


class MemoryFS:
    @staticmethod
    def zram_install():
        if not os.path.exists("/sys/class/zram-control"):
            logging.debug("[FS] Installing zram")
            return os.system("modprobe zram") == 0
        return True


    @staticmethod
    def zram_dev():
        logging.debug("[FS] Adding zram device")
        return open("/sys/class/zram-control/hot_add", "rt").read().strip("\n")


    def __init__(self, mount, disk, size="40M",
                 zram=True, zram_alg="lz4", zram_disk_size="100M",
                 zram_fs_type="ext4", rsync=True):
        self.mountpoint = mount
        self.disk = disk
        self.size = size
        self.zram = zram
        self.zram_alg = zram_alg
        self.zram_disk_size = zram_disk_size
        self.zram_fs_type = zram_fs_type
        self.zdev = None
        self.rsync = True
        self._setup()


    def _setup(self):
        if self.zram and MemoryFS.zram_install():
            # setup zram
            self.zdev = MemoryFS.zram_dev()
            open(f"/sys/block/zram{self.zdev}/comp_algorithm", "wt").write(self.zram_alg)
            open(f"/sys/block/zram{self.zdev}/disksize", "wt").write(self.zram_disk_size)
            open(f"/sys/block/zram{self.zdev}/mem_limit", "wt").write(self.size)
            logging.debug("[FS] Creating fs (type: %s)", self.zram_fs_type)
            os.system(f"mke2fs -t {self.zram_fs_type} /dev/zram{self.zdev} >/dev/null 2>&1")

        # ensure mountpoints exist
        if not os.path.exists(self.disk):
            logging.debug("[FS] Creating %s", self.disk)
            os.makedirs(self.disk)

        if not os.path.exists(self.mountpoint):
            logging.debug("[FS] Creating %s", self.mountpoint)
            os.makedirs(self.mountpoint)


    def daemonize(self, interval=60):
        logging.debug("[FS] Daemonized...")
        while True:
            self.sync()
            sleep(interval)


    def sync(self, to_ram=False):
        source, dest = (self.disk, self.mountpoint) if to_ram else (self.mountpoint, self.disk)
        needed, actually_free = size_of(source), shutil.disk_usage(dest)[2]
        if actually_free >= needed:
            logging.debug("[FS] Syncing %s -> %s", source,dest)
            if self.rsync:
                os.system(f"rsync -aXv --inplace --no-whole-file --delete-after {source}/ {dest}/ >/dev/null 2>&1")
            else:
                copy_tree(source, dest, preserve_symlinks=True)
            os.system("sync")
            return True
        return False


    def mount(self):
        if os.system(f"mount --bind {self.mountpoint} {self.disk}"):
            return False

        if os.system(f"mount --make-private {self.disk}"):
            return False

        if self.zram and self.zdev is not None:
            if os.system(f"mount -t {self.zram_fs_type} -o nosuid,noexec,nodev,user=pwnagotchi /dev/zram{self.zdev} {self.mountpoint}/"):
                return False
        else:
            if os.system(f"mount -t tmpfs -o nosuid,noexec,nodev,mode=0755,size={self.size} pwnagotchi {self.mountpoint}/"):
                return False

        return True


    def umount(self):
        if os.system(f"umount -l {self.mountpoint}"):
            return False

        if os.system(f"umount -l {self.disk}"):
            return False
        return True
