import subprocess
import os
import logging
import time
import pwnagotchi.ui.view as view

version = '1.1.0b'

_name = None


def set_name(new_name):
    if new_name is None:
        return

    new_name = new_name.strip()
    if new_name == '':
        return

    current = name()
    if new_name != current:
        global _name

        logging.info("setting unit hostname '%s' -> '%s'" % (current, new_name))
        with open('/etc/hostname', 'wt') as fp:
            fp.write(new_name)

        with open('/etc/hosts', 'rt') as fp:
            prev = fp.read()
            logging.debug("old hosts:\n%s\n" % prev)

        with open('/etc/hosts', 'wt') as fp:
            patched = prev.replace(current, new_name, -1)
            logging.debug("new hosts:\n%s\n" % patched)
            fp.write(patched)

        _name = new_name
        logging.info("restarting avahi ...")
        os.system("service avahi-daemon restart")
        logging.info("hostname set")


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
    out = subprocess.getoutput("free -m")
    for line in out.split("\n"):
        line = line.strip()
        if line.startswith("Mem:"):
            parts = list(map(int, line.split()[1:]))
            tot = parts[0]
            used = parts[1]
            free = parts[2]
            return used / tot

    return 0


def cpu_load():
    with open('/proc/stat', 'rt') as fp:
        for line in fp:
            line = line.strip()
            if line.startswith('cpu '):
                parts = list(map(int, line.split()[1:]))
                user_n = parts[0]
                sys_n = parts[2]
                idle_n = parts[3]
                tot = user_n + sys_n + idle_n
                return (user_n + sys_n) / tot
    return 0


def temperature(celsius=True):
    with open('/sys/class/thermal/thermal_zone0/temp', 'rt') as fp:
        temp = int(fp.read().strip())
    c = int(temp / 1000)
    return c if celsius else ((c * (9 / 5)) + 32)


def shutdown():
    logging.warning("shutting down ...")
    if view.ROOT:
        view.ROOT.on_shutdown()
        # give it some time to refresh the ui
        time.sleep(5)
    os.system("sync")
    os.system("halt")


def reboot():
    logging.warning("rebooting ...")
    os.system("sync")
    os.system("shutdown -r now")
