__author__ = 'evilsocket@gmail.com'
__version__ = '1.1.0'
__name__ = 'auto-update'
__license__ = 'GPL3'
__description__ = 'This plugin checks when updates are available and applies them when internet is available.'

import logging
import subprocess
import requests
import platform
import shutil
import glob

import pwnagotchi
import os
from pwnagotchi.utils import StatusFile

OPTIONS = dict()
READY = False
STATUS = StatusFile('/root/.auto-update')


def on_loaded():
    global READY
    if 'interval' not in OPTIONS or ('interval' in OPTIONS and OPTIONS['interval'] is None):
        logging.error("[update] main.plugins.auto-update.interval is not set")
        return
    READY = True
    logging.info("[update] plugin loaded.")


def check(version, repo, native=True):
    logging.debug("checking remote version for %s, local is %s" % (repo, version))
    info = {
        'repo': repo,
        'current': version,
        'available': None,
        'url': None,
        'native': native,
        'arch': platform.machine()
    }

    resp = requests.get("https://api.github.com/repos/%s/releases/latest" % repo)
    latest = resp.json()
    info['available'] = latest_ver = latest['tag_name'].replace('v', '')
    is_arm = info['arch'].startswith('arm')

    if latest_ver != info['current']:
        if not native:
            info['url'] = "https://github.com/%s/archive/%s.zip" % (repo, latest['tag_name'])
        else:
            # check if this release is compatible with arm6
            for asset in latest['assets']:
                download_url = asset['browser_download_url']
                if download_url.endswith('.zip') and (info['arch'] in download_url or (is_arm and 'armhf' in download_url)):
                    info['url'] = download_url
                    break

    return info


def install(display, update):
    name = update['repo'].split('/')[1]

    display.update(force=True, new_data={'status': 'Downloading %s ...' % name})

    path = os.path.join("/tmp/updates/", name)
    if os.path.exists(path):
        logging.debug("[update] deleting %s" % path)
        shutil.rmtree(path, ignore_errors=True, onerror=None)

    os.makedirs(path)

    target = "%s_%s.zip" % (name, update['available'])
    target_path = os.path.join(path, target)

    logging.info("[update] downloading %s to %s ..." % (update['url'], target_path))

    os.system('wget -q "%s" -O "%s"' % (update['url'], target_path))

    logging.info("[update] extracting %s to %s ..." % (target_path, path))

    display.update(force=True, new_data={'status': 'Extracting %s ...' % name})

    os.system('unzip "%s" -d "%s"' % (target_path, path))

    source_path = os.path.join(path, name)
    checksums = glob.glob("%s/*.sha256" % path)
    if len(checksums) == 0:
        if update['native']:
            logging.warning("native update without SHA256 checksum file")

    else:
        display.update(force=True, new_data={'status': 'Verifying %s ...' % name})

        checksum = checksums[0]

        logging.info("[update] verifying %s for %s ..." % (checksum, source_path))

        with open(checksums) as fp:
            expected = fp.read().strip().lower()

        real = subprocess.getoutput('sha256sum "%s"' % source_path).split(' ')[0].strip().lower()

        if real != expected:
            logging.warning("[update] checksum mismatch for %s: expected=%s got=%s" % (source_path, expected, real))
            return

    display.update(force=True, new_data={'status': 'Installing %s ...' % name})

    if update['native']:
        dest_path = subprocess.getoutput("which %s" % name)
        logging.info("[update] installing %s to %s ... TODO" % (source_path, dest_path))

    else:
        logging.info("[update] installing %s ... TODO" % source_path)


def on_internet_available(agent):
    global STATUS

    logging.debug("[update] internet connectivity is available (ready %s)" % READY)

    if READY:
        if STATUS.newer_then_hours(OPTIONS['interval']):
            logging.debug("[update] last check happened less than %d hours ago" % OPTIONS['interval'])
            return

        logging.info("[update] checking for updates ...")

        display = agent.view()
        prev_status = display.get('status')

        try:
            display.update(force=True, new_data={'status': 'Checking for updates ...'})

            to_install = []
            to_check = [
                (
                    'bettercap/bettercap', subprocess.getoutput('bettercap -version').split(' ')[1].replace('v', ''),
                    True),
                ('evilsocket/pwngrid', subprocess.getoutput('pwngrid -version').replace('v', ''), True),
                ('evilsocket/pwnagotchi', pwnagotchi.version, False)
            ]

            for repo, local_version, is_native in to_check:
                info = check(local_version, repo, is_native)
                if info['url'] is not None:
                    logging.warning("update for %s available: %s" % (repo, info['url']))
                    to_install.append(info)

            num_updates = len(to_install)
            if num_updates > 0:
                if OPTIONS['install']:
                    for update in to_install:
                        install(display, update)
                else:
                    prev_status = '%d new update%c available!' % (num_updates, 's' if num_updates > 1 else '')

            logging.info("[update] done")

            STATUS.update()

        except Exception as e:
            logging.error("[update] %s" % e)

        logging.debug("[update] setting status '%s'" % prev_status)
        display.update(force=True, new_data={'status': prev_status if prev_status is not None else ''})
