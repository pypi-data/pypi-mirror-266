#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

from functools import wraps

import flask
from joker.flasky.auth import HashedPassword
from pymongo.errors import DuplicateKeyError
from volkanic.errors import BusinessError

from cascadis.environ import GlobalInterface

gi = GlobalInterface()


class RequestBoundSingletonMeta(type):
    def __call__(cls, *args, **kwargs):
        import flask

        cache = flask.g.setdefault("request_bound_cache", {})
        try:
            return cache[cls]
        except KeyError:
            obj = super().__call__(*args, **kwargs)
            return cache.setdefault(cls, obj)


_builtin_users = {
    "admin": {
        "username": "admin",
        "password": (
            "50cbda2340ad708f307d1d9a7c084959bee68e6749651305ef44bf09c23e2888"
            ":sha256:cascadis"
        ),
    }
}


class LoginInterface(metaclass=RequestBoundSingletonMeta):
    def __init__(self, username: str, userinfo=None):
        self.username = username
        if userinfo:
            self.userinfo = userinfo  # noqa

    @classmethod
    def check(cls):
        if username := flask.session.get("username"):
            return cls(username)
        elif username := gi.conf.get("_auto_login_username"):
            return cls(username)
        else:
            raise BusinessError("You are not logged-in", "BE-0315")

    @staticmethod
    def install_builtin_users():
        coll = gi.mongodb.get_collection("users")
        if coll.find_one(projection=[]):
            return
        coll.create_index("username", unique=True)
        for userinfo in _builtin_users.values():
            try:
                coll.insert_one(userinfo)
            except DuplicateKeyError:
                print("failed:", userinfo)

    @classmethod
    def query(cls, username: str) -> dict | None:
        coll = gi.mongodb.get_collection("users")
        return coll.find_one({"username": username})

    @classmethod
    def login(cls, username: str, password: str):
        userinfo = cls.query(username)
        err_login = BusinessError("Wrong username or password", "LoginFailed")
        if not userinfo:
            raise err_login
        h_password = userinfo.pop("password")
        hp = HashedPassword.parse(h_password)
        if not hp.verify(password):
            raise err_login
        flask.session["username"] = username
        return cls(username, userinfo)


def login_required(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        LoginInterface.check()
        return func(*args, **kwargs)

    return decorated_func


def set_protection_level(level: int):
    """
    If a view function has protection level higher
    than gi.conf['accessibility'], the user has to
    log in to access it.
    """

    def _decorator(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            if gi.conf["accessibility"] < level:
                LoginInterface.check()
            return func(*args, **kwargs)

        return decorated_func

    return _decorator
