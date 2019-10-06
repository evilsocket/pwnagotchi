#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import pwnagotchi

required = []
with open('requirements.txt') as fp:
    for line in fp:
        line = line.strip()
        if line != "":
            required.append(line)

setup(name='pwnagotchi',
      version=pwnagotchi.version,
      description='(⌐■_■) - Deep Reinforcement Learning instrumenting bettercap for WiFI pwning.',
      author='evilsocket && the dev team',
      author_email='evilsocket@gmail.com',
      url='https://pwnagotchi.ai/',
      license='GPL',
      install_requires=required,
      scripts=['bin/pwnagotchi'],
      package_data={'pwnagotchi': ['defaults.yml', 'pwnagotchi/defaults.yml']},
      include_package_data=True,
      packages=find_packages(),
      classifiers=[
          'Programming Language :: Python :: 3',
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Environment :: Console',
      ])
