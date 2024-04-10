#!/usr/bin/env python3
# coding: utf-8

import os
import sys

from bson import ObjectId

from cascadis.environ import GlobalInterface
from cascadis.solutions import register_and_query

gi = GlobalInterface()


def oid_to_date(oid: ObjectId):
    dt = oid.generation_time
    return dt.strftime("%Y-%m-%d_%H:%M:%S")


def fmt_register_record(rec: dict):
    _id = rec["_id"]
    date = oid_to_date(_id)
    file_id = rec["file_id"]
    path = rec["path"]
    path_flag = "+" if os.path.isfile(path) else "-"
    new_flag = "*" if rec.get("_new") else " "
    return f"{file_id} {new_flag}{date} {path_flag} {path}"


def read_file(path):
    blksize = 1024 * 1024
    with open(path, "rb") as fin:
        blk = fin.read(blksize)
        while blk:
            yield blk
            blk = fin.read(blksize)


def main():
    for path in sys.argv[1:]:
        path = os.path.abspath(path)
        file_id = gi.cas.save(read_file(path))
        for rec in register_and_query(file_id, path):
            print(fmt_register_record(rec))
        print()


if __name__ == "__main__":
    main()
