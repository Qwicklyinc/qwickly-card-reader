#!/usr/bin/env python3

import os
import shutil
from pkg_resources import parse_version


def current_version():
    os.chdir('/home/pi/qwickly')
    p = os.popen('git describe --tags')
    version = p.read()
    return version.strip()


def update_available():
    pass


def get_version(version):
    pass


def update():
    pass