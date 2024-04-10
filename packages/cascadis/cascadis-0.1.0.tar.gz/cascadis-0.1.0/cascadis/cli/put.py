#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from joker.cast.iterative import chunkwize

from cascadis.environ import GlobalInterface
from cascadis.solutions import register_cli_upload
from cascadis.utils import find_regular_files

gi = GlobalInterface()


class _CommandContext:
    def __init__(self, delete=False):
        self.delete = delete

    def _put_file_into_cas(self, path: str):
        if self.delete and os.stat(path).st_dev == os.stat(gi.files).st_dev:
            return gi.cas.seize(path)
        with open(path, "rb") as fin:
            content = fin.read()
            cid = gi.cas.save([content])
        if self.delete:
            os.remove(path)
        return cid

    def put_file_into_cas(self, path: str):
        path = os.path.abspath(path)
        cid = self._put_file_into_cas(path)
        print(cid, path)
        register_cli_upload(cid, path)
        return cid

    def put_files_in_dir_into_cas(self, dirpath):
        executor = ThreadPoolExecutor(max_workers=10)
        paths = find_regular_files(dirpath)
        for batch in chunkwize(1000, paths):
            executor.map(self.put_file_into_cas, batch)


def _main(paths: list[str], delete=False):
    cc = _CommandContext(delete=delete)
    for path in paths:
        if os.path.isdir(path):
            cc.put_files_in_dir_into_cas(path)
        else:
            cc.put_file_into_cas(path)


def main(prog: str, args: list[str]):
    desc = "Put files into Cascadis."
    pr = argparse.ArgumentParser(prog=prog, description=desc)
    pr.add_argument(
        "-D",
        "--delete",
        action="store_true",
        help="delete source files",
    )
    pr.add_argument(
        "files",
        metavar="path",
        nargs="*",
        help="source file",
    )
    ns = pr.parse_args(args)
    _main(ns.files, delete=ns.delete)


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
