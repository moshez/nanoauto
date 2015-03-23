# Copyright (c) Moshe Zadka
# See LICENSE for details.
from distutils import cmd, spawn

import os
import subprocess
import sys

import setuptools

import nanoauto as module

setuptools.setup(
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Twisted',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Topic :: System',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='editor web twisted',
    packages=[module.__name__, 'twisted.plugins'],
    install_requires=['Twisted', 'ncolony', 'klein'],
    extras_require = {
        'dev': ['wheel'],
    },
    **module.metadata
)
