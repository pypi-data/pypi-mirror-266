#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import threading

from magic import Magic

from cascadis.environ import GlobalInterface

gi = GlobalInterface()
_thread_local = threading.local()
_thread_local.magic = Magic(mime=True, mime_encoding=True)


def _get_magic() -> Magic:
    try:
        return _thread_local.magic
    except AttributeError:
        _thread_local.magic = Magic(mime=True, mime_encoding=True)
        return _thread_local.magic


def infer_content_type(cid: str) -> str:
    path = gi.cas.locate(cid)
    return _get_magic().from_file(path)


def get_or_infer_content_type(cid: str) -> str:
    record = gi.mongodb["objects"].find_one(
        {"_id": cid, "content_type": {"$exists": True}},
    )
    if record:
        return record["content_type"]
    content_type = infer_content_type(cid)
    gi.mongodb["objects"].update_one(
        {"_id": cid},
        {"$set": {"content_type": content_type}},
        upsert=True,
    )
    return content_type
