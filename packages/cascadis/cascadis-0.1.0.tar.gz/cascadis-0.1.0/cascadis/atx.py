#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import os
import time

from volkanic.utils import ignore_arguments

from cascadis.auth import LoginInterface
from cascadis.environ import GlobalInterface

gi = GlobalInterface()


def remove_legacy_files():
    ttl = gi.conf["cache_ttl"]
    if not ttl:
        return
    now = time.time()
    for path in gi.cas.iter_paths():
        mtime = os.path.getmtime(path)
        if now - mtime > ttl:
            os.remove(path)


@ignore_arguments
def main():
    LoginInterface.install_builtin_users()
    while True:
        time.sleep(3600)
        remove_legacy_files()
