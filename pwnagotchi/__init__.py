import os
import logging
import time
import re



from pwnagotchi._version import __version__

_name = None
config = None


def set_name(new_name):
    if new_name is None:
        return

    new_name = new_name.strip()
    if new_name == '':
        return

    if not re.match(r'^[a-zA-Z0-9\-]{2,25}$', new_name):
        logging.warning("name '%s' is invalid: min length is 2, max length 25, only a-zA-Z0-9- allowed", new_name)
        return

    current = name()
    if new_name != current:
        global _name

        logging.info("setting unit hostname '%s' -> '%s'", current, new_name)
        with open('/etc/hostname', 'wt') as fp:
            fp.write(new_name)

        with open('/etc/hosts', 'rt') as fp:
            prev = fp.read()
            logging.debug("old hosts:\n%s\n", prev)

        with open('/etc/hosts', 'wt') as fp:
            patched = prev.replace(current, new_name, -1)
            logging.debug("new hosts:\n%s\n", patched)
            fp.write(patched)

        os.system("hostname '%s'" % new_name)
        pwnagotchi.reboot()


def name():
    global _name
    if _name is None:
        with open('/etc/hostname', 'rt') as fp:
            _name = fp.read().strip()
    return _name


def uptime():
    with open('/proc/uptime') as fp:
        return int(fp.read().split('.')[0])


def mem_usage():
    with open('/proc/meminfo') as fp:
        for line in fp:
            line = line.strip()
            if line.startswith("MemTotal:"):
                kb_mem_total = int(line.split()[1])
            if line.startswith("MemFree:"):
                kb_mem_free = int(line.split()[1])
            if line.startswith("Buffers:"):
                kb_main_buffers = int(line.split()[1])
            if line.startswith("Cached:"):
                kb_main_cached = int(line.split()[1])
        kb_mem_used = kb_mem_total - kb_mem_free - kb_main_cached - kb_main_buffers
        return round(kb_mem_used / kb_mem_total, 1)

    return 0


def _cpu_stat():
    """
    Returns the splitted first line of the /proc/stat file
    """
    with open('/proc/stat', 'rt') as fp:
        return list(map(int,fp.readline().split()[1:]))


def cpu_load():
    """
    Returns the current cpuload
    """
    parts0 = _cpu_stat()
    time.sleep(0.1)
    parts1 = _cpu_stat()
    parts_diff = [p1 - p0 for (p0, p1) in zip(parts0, parts1)]
    user, nice, sys, idle, iowait, irq, softirq, steal, _guest, _guest_nice = parts_diff
    idle_sum = idle + iowait
    non_idle_sum = user + nice + sys + irq + softirq + steal
    total = idle_sum + non_idle_sum
    return non_idle_sum / total


def temperature(celsius=True):
    with open('/sys/class/thermal/thermal_zone0/temp', 'rt') as fp:
        temp = int(fp.read().strip())
    c = int(temp / 1000)
    return c if celsius else ((c * (9 / 5)) + 32)


def shutdown():
    logging.warning("shutting down ...")

    from pwnagotchi.ui import view
    if view.ROOT:
        view.ROOT.on_shutdown()
        # give it some time to refresh the ui
        time.sleep(10)

    logging.warning("syncing...")

    from pwnagotchi import fs
    for m in fs.mounts:
        m.sync()
 
    os.system("sync")
    os.system("halt")


def restart(mode):
    logging.warning("restarting in %s mode ...", mode)

    if mode == 'AUTO':
        os.system("touch /root/.pwnagotchi-auto")
    else:
        os.system("touch /root/.pwnagotchi-manual")

    os.system("service bettercap restart")
    os.system("service pwnagotchi restart")


def reboot(mode=None):
    if mode is not None:
        mode = mode.upper()
        logging.warning("rebooting in %s mode ...", mode)
    else:
        logging.warning("rebooting ...")

    from pwnagotchi.ui import view
    if view.ROOT:
        view.ROOT.on_rebooting()
        # give it some time to refresh the ui
        time.sleep(10)

    if mode == 'AUTO':
        os.system("touch /root/.pwnagotchi-auto")
    elif mode == 'MANU':
        os.system("touch /root/.pwnagotchi-manual")

    logging.warning("syncing...")

    from pwnagotchi import fs
    for m in fs.mounts:
        m.sync()

    os.system("sync")
    os.system("shutdown -r now")
