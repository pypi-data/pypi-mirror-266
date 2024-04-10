#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from joker.cast.iterative import chunkwize
from volkanic.utils import printerr

from cascadis.environ import GlobalInterface

gi = GlobalInterface()


class _CommandContext:
    def __init__(self, overwrite=False):
        self.overwrite = overwrite

    def get_file_from_cas(self, cid: str, path: str):
        dir_ = os.path.split(path)[0]
        os.makedirs(dir_, exist_ok=True)
        exists = os.path.exists(path)
        if not self.overwrite and exists:
            print(cid, "SKIPPED", path)
            return
        with open(path, "wb") as fout:
            for chunk in gi.cas.load(cid):
                fout.write(chunk)
        action = "OVERWRITTEN" if exists else "CREATED"
        print(cid, action, path)

    def _get_file_from_cas_with_one_arg(self, pair: tuple[str, str]):
        self.get_file_from_cas(*pair)

    def get_files_from_cas(self, pairs: list[tuple[str, str]]):
        executor = ThreadPoolExecutor(max_workers=10)
        for batch in chunkwize(1000, pairs):
            executor.map(self._get_file_from_cas_with_one_arg, batch)


def main(_prog: str, args: list[str]):
    desc = "Get files from Cascadis."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "-O",
        "--overwrite",
        action="store_true",
        help="overwrite existing files",
    )
    parser.add_argument("cid", help="content identifier")
    parser.add_argument("path", help="file to be created")
    parser.add_argument(
        "more",
        nargs="*",
        default=[],
        help="more cid and path pairs",
    )
    ns = parser.parse_args(args)
    if len(ns.more) % 2:
        printerr("error: wrong number of arguments")
        sys.exit(1)
    pairs = chunkwize(2, [ns.cid, ns.path] + ns.more)
    _CommandContext(ns.overwrite).get_files_from_cas(list(pairs))


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
