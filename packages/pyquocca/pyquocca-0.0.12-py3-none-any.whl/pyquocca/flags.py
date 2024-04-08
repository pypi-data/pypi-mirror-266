import logging
import os
from typing import Optional

import requests

from .header_utils import get_username

logger = logging.getLogger(__name__)

FLAGANIZER_URL = os.getenv("FLAGANIZER_URL")
dummy = FLAGANIZER_URL is None
if dummy:
    logger.warn(
        "FLAGANIZER_URL environment variable not found, generating dummy flags."
    )
else:
    FLAGANIZER_URL = FLAGANIZER_URL.removesuffix("/")


class FlaganizerException(Exception):
    pass


class MissingTokenError(FlaganizerException):
    def __init__(self, key: str):
        super().__init__(f"This service does not have access to the token for {key}.")


def _get_token(key: str) -> str:
    try:
        with open(f"/run/secrets/flaganizer/{key}/token") as f:
            return f.read()
    except FileNotFoundError as e:
        raise MissingTokenError(key) from e


def get_flag(key: str, username: Optional[str] = None) -> str:
    if dummy:
        return f"FLAG{{{key}}}"

    if username is None:
        username = get_username()
        if username is None:
            raise ValueError("Must be running with a user or request.")

    assert FLAGANIZER_URL is not None, "flaganizer url missing"
    r = requests.get(
        f"{FLAGANIZER_URL}/generate",
        params={"username": username},
        headers={
            "Authorization": f"Bearer {_get_token(key)}",
            "User-Agent": "pyquocca",
        },
    )
    if r.status_code == 200:
        return r.json().get("flag")
    else:
        raise FlaganizerException(r.json().get("msg"))
