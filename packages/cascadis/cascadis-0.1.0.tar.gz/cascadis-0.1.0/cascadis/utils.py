#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import os


def find_regular_files(dirpath, **kwargs):
    for root, dirs, files in os.walk(dirpath, **kwargs):
        for name in files:
            path = os.path.join(root, name)
            if os.path.isfile(path):
                yield path
