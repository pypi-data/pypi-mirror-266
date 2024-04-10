#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import datetime
import logging
import mimetypes
import os
from typing import Iterable, TypedDict

import pymongo.errors
from flask import request

from cascadis.environ import GlobalInterface
from cascadis.solutions.inference import get_or_infer_content_type
from cascadis.solutions.legacy import (
    infer_mimetype_from_upload,
    infer_mimetype_with_file_command,
)

gi = GlobalInterface()
_logger = logging.getLogger(__name__)


def query_by_file_id(file_id):
    coll = gi.mongodb.get_collection("file_registry")
    cursor = coll.find({"file_id": file_id})
    return list(cursor)


def legacy_register(file_id, path, ttl=86400):
    coll = gi.mongodb["file_registry"]
    now = datetime.datetime.now()
    expired_at = now + datetime.timedelta(seconds=ttl)
    record = {
        "file_id": file_id,
        "path": path,
        "created_at": now,
        "expired_at": expired_at,
    }
    try:
        ir = coll.insert_one(record)
    except pymongo.errors.DuplicateKeyError:
        return
    return ir.inserted_id


def register_and_query(file_id, path):
    reg_id = legacy_register(file_id, path)
    coll = gi.mongodb.get_collection("file_registry")
    for rec in coll.find({"_id": reg_id}):
        rec["_new"] = True
        yield rec
    yield from coll.find({"file_id": file_id, "_id": {"$ne": reg_id}})


def read_uploading_file(chunksize=16384) -> Iterable[bytes]:
    fup = request.files.get("file")
    while chunk := fup.stream.read(chunksize):
        yield chunk


class UploadRecord(TypedDict):
    cid: str
    method: str
    username: str
    mimetype: str | None
    filename: str | None


def register_object(cid: str, mimetype: str):
    coll = gi.mongodb["objects"]
    coll.update_one(
        {"_id": cid},
        {"$set": {"mimetype": mimetype, "_id": cid}},
        upsert=True,
    )


def register_http_upload(cid: str):
    coll = gi.mongodb["uploads"]
    fup = request.files.get("file")
    record: UploadRecord = {
        "cid": cid,
        "method": "http",
        "username": "admin",
        "mimetype": fup.mimetype,
        "filename": fup.filename,
    }
    coll.insert_one(record)
    register_object(cid, fup.mimetype)


def register_cli_upload(cid: str, filename: str):
    coll = gi.mongodb["uploads"]
    mimetype = mimetypes.guess_type(filename)[0]
    record: UploadRecord = {
        "cid": cid,
        "method": "cli",
        "username": os.getlogin(),
        "mimetype": mimetype,
        "filename": filename,
    }
    coll.insert_one(record)
    if mimetype:
        register_object(cid, mimetype)


if __name__ == "__main__":
    print(
        infer_mimetype_with_file_command(
            "3543069d447f8ef042b5f0500e36a9b787f9288a064dd38905f4147169f9c476"
        )
    )
    print(
        infer_mimetype_from_upload(
            "3543069d447f8ef042b5f0500e36a9b787f9288a064dd38905f4147169f9c476"
        )
    )
