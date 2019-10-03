import subprocess

_name = None


def name():
    global _name
    if _name is None:
        with open('/etc/hostname', 'rt') as fp:
            _name = fp.read().strip()
    return _name


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
