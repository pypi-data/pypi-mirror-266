#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import dataclasses
import datetime
import random
from string import ascii_uppercase
from typing import Self

from cascadis.solutions import gi, _logger, get_or_infer_content_type


def create_indexes():
    c = gi.mongodb["sessions"]
    c.create_index("session_id", unique=True)
    c.create_index("expires_at", expireAfterSeconds=300)


@dataclasses.dataclass
class Session:
    cid: str
    # TODO: rename to sid?
    sid: str
    content_type: str
    filename: str
    expires_at: datetime.datetime

    @classmethod
    def load(cls, sid: str) -> Self:
        filtr = {
            "sid": sid,
            # do not rely on TTL index of mongodb
            "expires_at": {
                "$gt": datetime.datetime.now(),
            },
        }
        c = gi.mongodb["sessions"]
        record = c.find_one(filtr, projection={"_id": False})
        if record is None:
            raise FileNotFoundError(f"session not found: {sid}")
        return cls(**record)

    def save(self):
        record = dataclasses.asdict(self)
        ir = gi.mongodb["sessions"].insert_one(record)
        _logger.info("session saved: %s, %s", ir.inserted_id, self.sid)

    @classmethod
    def create(
        cls,
        cid: str,
        content_type: str = None,
        filename: str = None,
        ttl: int = 60,
    ) -> Self:
        if content_type is None:
            content_type = get_or_infer_content_type(cid)
        session_id = "".join(random.choices(ascii_uppercase, k=20))
        expires_at = datetime.datetime.now() + datetime.timedelta(seconds=ttl)
        return cls(cid, session_id, content_type, filename, expires_at)

    @staticmethod
    def remove_expired():
        """an alternative way to remove expired record"""
        gi.mongodb["sessions"].delete_many(
            {"expires_at": {"$lt": datetime.datetime.now()}}
        )
