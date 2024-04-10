#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import argparse
import sys
import time
import traceback

import flask

# noinspection PyPackageRequirements
import werkzeug.exceptions
from flask import request
from flask.json.provider import DefaultJSONProvider
from joker.flasky.viewutils import (
    json_default_strict,
    chain_json_default_functions,
)
from volkanic.errors import KnownError
from volkanic.introspect import ErrorInfo

import cascadis.views
from cascadis.environ import GlobalInterface

gi = GlobalInterface()


class JSONProvider(DefaultJSONProvider):
    default = chain_json_default_functions(
        json_default_strict,
        DefaultJSONProvider.default,
        str,
    )


class FlaskApplication(flask.Flask):
    json_provider_class = JSONProvider


app = FlaskApplication(__name__)
app.secret_key = "TfT2T6UA1BTdk7HCIGmpvcmFTla45jYE2QKIiys4AAEGQxAt09Trc71JyM"


@app.errorhandler(KnownError)
def on_known_error(error: KnownError):
    if request.files:
        time.sleep(1)
    return error.to_dict()


@app.errorhandler(Exception)
def on_other_error(_error: Exception):
    # https://flask.palletsprojects.com/en/2.0.x/errorhandling/#generic-exception-handlers
    if isinstance(_error, werkzeug.exceptions.HTTPException):
        return _error
    traceback.print_exc()
    errinfo = ErrorInfo()
    return errinfo.to_dict()


# app.use_default_error_handlers(gi.error_interface)
app.register_blueprint(cascadis.views.bp)


def main(prog: str, args: list[str]):
    msg = (
        "For production, run with gunicorn or uwsgi:\n"
        "gunicorn -w 8 cascadis.api:app -b 0.0.0.0:16000"
    )
    print(msg)
    desc = "run cascadis web service"
    pr = argparse.ArgumentParser(prog=prog, description=desc, add_help=False)
    add = pr.add_argument
    add("--help", action="help", help="show this help message and exit")
    add("-h", "--host", help="hostname", default="127.0.0.1")
    add("-p", "--port", type=int, help="port number", default=16000)
    ns = pr.parse_args(args)
    app.run(ns.host, ns.port, debug=True)


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
