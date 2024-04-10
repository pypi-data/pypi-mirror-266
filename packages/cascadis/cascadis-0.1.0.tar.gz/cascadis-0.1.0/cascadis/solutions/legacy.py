#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import re
import subprocess

from cascadis.environ import GlobalInterface

gi = GlobalInterface()

# e.g. "pixels.jpg: image/jpeg; charset=binary"
_file_cmd_output_regex = re.compile(r":\s*(\w+/\w+; charset=\w+)$")


def infer_mimetype_from_upload(cid: str) -> str:
    coll = gi.mongodb["uploads"]
    record = coll.find_one(
        {"cid": cid},
        sort=[("_id", -1)],
        projection=["mimetype"],
    )
    if record:
        return record["mimetype"]


def infer_mimetype_with_file_command(cid: str) -> str:
    path = gi.cas.locate(cid)
    cmd = ["file", "--mime-type", str(path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.stdout.split(":", maxsplit=1)[-1]


def infer_content_type_with_file_command(cid: str) -> str:
    path = gi.cas.locate(cid)
    cmd = ["file", "--mime", str(path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    mat = _file_cmd_output_regex.search(proc.stdout.strip())
    if mat is None:
        return "application/octet-stream"
    return mat.group(1)


def infer_mimetype(cid: str):
    if mimetype := infer_mimetype_from_upload(cid):
        return mimetype
    if mimetype := infer_mimetype_with_file_command(cid):
        return mimetype
    return "application/octet-stream"


