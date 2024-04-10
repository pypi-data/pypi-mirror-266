#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import logging
import mimetypes
import os.path

import flask
from flask import Blueprint, request, Response

from cascadis.auth import set_protection_level, LoginInterface
from cascadis.environ import GlobalInterface
from cascadis.solutions import register_http_upload
from cascadis.solutions.sessions import Session
from cascadis.viewutils import (
    Proxy, fmt_content_disposition
)

gi = GlobalInterface()
bp = Blueprint("cas", __name__)
_logger = logging.getLogger(__name__)


def _read_uploading_file_in_chunks(chunksize=16384):
    fup = request.files.get("file")
    while chunk := fup.stream.read(chunksize):
        yield chunk


@bp.route("/")
@set_protection_level(1)
def api_index():
    import cascadis

    return {
        "code": 0,
        "data": {
            "project": gi.project_name,
            "version": cascadis.__version__,
            "homepage": "https://github.com/frozflame/cascadis",
            "cache_ttl": gi.conf["cache_ttl"],
        },
    }


@bp.route("/cas/login", methods=["GET", "POST"])
@bp.route("/cascadis/login", methods=["GET", "POST"])
def api_login():
    if request.method == "GET":
        # TODO: or use joker.flasky.pages?
        # pages.respond_login_page(**gi.conf["test_account"])
        return flask.render_template("login.html", **gi.conf["test_account"])
    LoginInterface.install_builtin_users()
    username = request.form["username"]
    password = request.form["password"]
    li = LoginInterface.login(username, password)
    return {"code": 0, "data": li.userinfo}


@bp.route("/cas/files", methods=["GET", "POST"])
@bp.route("/cascadis/files", methods=["GET", "POST"])
@set_protection_level(2)
def api_upload():
    # if request.method == "GET":
    #     return pages.respond_upload_page()
    # chunks = read_uploading_file()
    if request.method == "GET":
        return flask.render_template("upload.html")
    chunks = _read_uploading_file_in_chunks()
    cid = gi.cas.save(chunks)
    register_http_upload(cid)
    return {"code": 0, "data": cid}


def _respond_xaccel_redirect(key: str, ext: str, contenttype: str):
    # nginx: http://wiki.nginx.org/NginxXSendfile
    resp = flask.make_response()
    rel_path = gi.cas.locate(key).relative_to(gi.files)
    headers = {
        "X-Accel-Redirect": str(rel_path),
        "Cache-Control": "no-cache",
        "Content-Type": contenttype,
        "Content-Disposition": f"attachment; filename={key}{ext}",
    }
    resp.headers.update(headers)
    return resp


@bp.route("/cas/files/<cname>")
@bp.route("/cascadis/files/<cname>")
@bp.route("/cas/c/<cname>")
@bp.route("/cascadis/content/<cname>")
@set_protection_level(1)
def api_download(cname: str):
    # TODO: support Content-Length on GET/HEAD
    # TODO: use HEAD method on HEAD proxy
    cid, ext = os.path.splitext(cname)
    if len(cid) != 64:
        return flask.abort(404)
    if not gi.cas.exists(cid):
        if upstream := gi.conf["upstream"]:
            proxy = Proxy(upstream, gi.conf["proxy_ttl"])
            return proxy.forward(cname)
        return flask.abort(404)
    default_mimetype = "application/octet-stream"
    filename = request.args.get("filename", cname)
    mimetype = mimetypes.guess_type(filename)[0] or default_mimetype
    if gi.conf["use_nginx"]:
        return _respond_xaccel_redirect(cid, ext, mimetype)
    if request.method == "HEAD":
        chunks = []
    else:
        chunks = gi.cas.load(cid)
    # https://flask.palletsprojects.com/en/2.1.x/patterns/streaming/#basic-usage
    resp = Response(chunks, mimetype=mimetype)
    if mimetype == default_mimetype:
        resp.headers["Content-Disposition"] = "inline"
    elif filename != cname:
        content_dispos = fmt_content_disposition(filename, attachment=True)
        resp.headers["Content-Disposition"] = content_dispos
    return resp


@bp.route("/cas/s/<session_id>")
@bp.route("/cascadis/session/<session_id>")
def view_public(session_id):
    try:
        session = Session.load(session_id)
    except FileNotFoundError:
        return flask.abort(404)
    chunks = gi.cas.load(session.cid)
    print(session, "----")
    return Response(chunks, content_type=session.content_type)
