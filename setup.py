#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
import glob
import shutil

setup_path = os.path.dirname(__file__)
data_path = os.path.join(setup_path, "builder/data")

for source_filename in glob.glob("%s/**" % data_path, recursive=True):
    if os.path.isfile(source_filename):
        dest_filename = source_filename.replace(data_path, '')
        dest_folder = os.path.dirname(dest_filename)

        print("installing %s to %s ..." % (source_filename, dest_filename))
        try:
            if not os.path.isdir(dest_folder):
                os.makedirs(dest_folder)

            shutil.copyfile(source_filename, dest_filename)
        except Exception as e:
            print("error installing %s: %s" % (source_filename, e))

# reload systemd units
os.system("systemctl daemon-reload")

required = []
with open('requirements.txt') as fp:
    for line in fp:
        line = line.strip()
        if line != "":
            required.append(line)

import pwnagotchi

setup(name='pwnagotchi',
      version=pwnagotchi.version,
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
