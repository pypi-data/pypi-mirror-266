#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import dataclasses
import urllib.parse

import flask
import requests
from flask import request, Response


@dataclasses.dataclass
class Proxy:
    base_url: str
    default_ttl: int = 5

    def get_ttl(self) -> int:
        key = "X-Proxy-TTL"
        return request.headers.get(key, default=self.default_ttl, type=int)

    def fetch(self, filename: str) -> requests.Response | None:
        url = urllib.parse.urljoin(self.base_url, f"files/{filename}")
        ttl = self.get_ttl() - 1
        if not ttl:
            return
        resp = requests.get(url, headers={"X-Proxy-TTL": str(ttl)})
        if resp.status_code == 404:
            return
        return resp

    def forward(self, filename: str) -> Response:
        resp = self.fetch(filename)
        if resp is None:
            return flask.abort(404)
        ret_resp = Response(
            resp.content,
            content_type=resp.headers["Content-Type"],
        )
        if disposition := resp.headers.get("Content-Disposition"):
            ret_resp.headers["Content-Disposition"] = disposition
        return ret_resp


def fmt_content_disposition(filename: str, attachment=False) -> str:
    quoted = urllib.parse.quote(filename)
    kind = "attachment" if attachment else "inline"
    return f'''{kind}; filename="{quoted}"; filename*="UTF-8''{quoted}"'''


def fmt_content_disposition_attachment(filename: str) -> str:
    return fmt_content_disposition(filename, attachment=True)
