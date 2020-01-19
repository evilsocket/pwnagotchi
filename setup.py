#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from distutils.util import strtobool
import os
import glob
import shutil
import re


def install_file(source_filename, dest_filename):
    # do not overwrite network configuration if it exists already
    # https://github.com/evilsocket/pwnagotchi/issues/483
    if dest_filename.startswith('/etc/network/interfaces.d/') and os.path.exists(dest_filename):
        print("%s exists, skipping ..." % dest_filename)
        return

    print("installing %s to %s ..." % (source_filename, dest_filename))
    try:
        dest_folder = os.path.dirname(dest_filename)
        if not os.path.isdir(dest_folder):
            os.makedirs(dest_folder)

        shutil.copyfile(source_filename, dest_filename)
    except Exception as e:
        print("error installing %s: %s" % (source_filename, e))


def install_system_files():
    setup_path = os.path.dirname(__file__)
    data_path = os.path.join(setup_path, "builder/data")

    for source_filename in glob.glob("%s/**" % data_path, recursive=True):
        if os.path.isfile(source_filename):
            dest_filename = source_filename.replace(data_path, '')
            install_file(source_filename, dest_filename)

    # reload systemd units
    os.system("systemctl daemon-reload")


def installer():
    install_system_files()
    # for people updating https://github.com/evilsocket/pwnagotchi/pull/551/files
    os.system("systemctl enable fstrim.timer")

def version(version_file):
    with open(version_file, 'rt') as vf:
        version_file_content = vf.read()

    version_match = re.search(r"__version__\s*=\s*[\"\']([^\"\']+)", version_file_content)
    if version_match:
        return version_match.groups()[0]

    return None


if strtobool(os.environ.get("PWNAGOTCHI_ENABLE_INSTALLER", "1")):
    installer()

with open('requirements.txt') as fp:
    required = [line.strip() for line in fp if line.strip() != ""]

VERSION_FILE = 'pwnagotchi/_version.py'
pwnagotchi_version = version(VERSION_FILE)

setup(name='pwnagotchi',
      version=pwnagotchi_version,
      description='(⌐■_■) - Deep Reinforcement Learning instrumenting bettercap for WiFI pwning.',
      author='evilsocket && the dev team',
      author_email='evilsocket@gmail.com',
      url='https://pwnagotchi.ai/',
      license='GPL',
      install_requires=required,
      scripts=['bin/pwnagotchi'],
      package_data={'pwnagotchi': ['defaults.yml', 'pwnagotchi/defaults.yml', 'locale/*/LC_MESSAGES/*.mo']},
      include_package_data=True,
      packages=find_packages(),
      classifiers=[
          'Programming Language :: Python :: 3',
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Environment :: Console',
      ])
