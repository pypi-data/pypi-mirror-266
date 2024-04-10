#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import joker.filesys.cas
from joker.filesys import utils
from joker.filesys.utils import Pathlike, checksum_hexdigest


class ContentAddressedStorage(joker.filesys.cas.ContentAddressedStorage):
    def seize(self, path: Pathlike) -> str:
        cid = checksum_hexdigest(path, "sha256")
        utils.moves(path, self.locate(cid))
        return cid
