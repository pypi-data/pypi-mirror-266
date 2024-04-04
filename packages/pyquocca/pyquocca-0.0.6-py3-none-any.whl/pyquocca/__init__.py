import os
from typing import Optional

import requests
from flask import request as flask_request
from flask.wrappers import Request

FLAGANIZER_HOST = os.getenv("FLAGANIZER_HOST")

USERNAME_HEADER = "X-mTLS-Username"
STAFF_HEADER = "X-mTLS-Staff"
FIRST_NAME_HEADER = "X-mTLS-First-Name"
LAST_NAME_HEADER = "X-mTLS-Last-Name"
FULL_NAME_HEADER = "X-mTLS-Full-Name"
IMPERSONATED_BY_HEADER = "X-mTLS-Impersonated-By"

XSSBOT_NAME = "XSSBot"


def get_username(request: Optional[Request] = None) -> Optional[str]:
    r = request if request is not None else flask_request
    return r.headers.get(USERNAME_HEADER, None)


def get_impersonator(request: Optional[Request] = None) -> Optional[str]:
    r = request if request is not None else flask_request
    return r.headers.get(IMPERSONATED_BY_HEADER, None)


def is_staff(request: Optional[Request] = None) -> bool:
    r = request if request is not None else flask_request
    return r.headers.get(STAFF_HEADER, "false") == "true"


def is_xssbot(request: Optional[Request] = None) -> bool:
    r = request if request is not None else flask_request
    return (is_staff(r) and get_username(r) == XSSBOT_NAME) or (
        get_impersonator() == XSSBOT_NAME
    )


def get_first_name(request: Optional[Request] = None) -> Optional[str]:
    r = request if request is not None else flask_request
    return r.headers.get(FIRST_NAME_HEADER, get_username(request))


def get_last_name(request: Optional[Request] = None) -> Optional[str]:
    r = request if request is not None else flask_request
    return r.headers.get(LAST_NAME_HEADER, get_username(request))


def get_full_name(request: Optional[Request] = None) -> Optional[str]:
    r = request if request is not None else flask_request
    return r.headers.get(FULL_NAME_HEADER, get_username(request))


class FlaganizerException(Exception):
    pass


class MissingTokenError(FlaganizerException):
    def __init__(self, key: str):
        super().__init__(f"This service does not have access to the token for {key}.")


def get_token(key: str) -> str:
    try:
        with open(f"/run/secrets/flaganizer/{key}/token") as f:
            return f.read()
    except FileNotFoundError as e:
        raise MissingTokenError(key) from e


def get_flag(key: str, username: Optional[str] = None) -> str:
    if username is None:
        username = get_username()
        if username is None:
            raise ValueError("Must be running with a user or request.")

    assert FLAGANIZER_HOST is not None, "flaganizer host missing"
    r = requests.get(
        f"http://{FLAGANIZER_HOST}/generate",
        params={"username": username},
        headers={
            "Authorization": f"Bearer {get_token(key)}",
            "User-Agent": "pyquocca",
        },
    )
    if r.status_code == 200:
        return r.json().get("flag")
    else:
        raise FlaganizerException(r.json().get("msg"))
