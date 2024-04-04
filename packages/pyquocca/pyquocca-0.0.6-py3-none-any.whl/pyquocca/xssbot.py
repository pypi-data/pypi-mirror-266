import os
from typing import Any, Literal, Optional

import requests
from typing_extensions import NotRequired, TypedDict

from . import get_username, is_staff

XSSBOT_HOST = os.getenv("XSSBOT_HOST")
XSSBOT_URL = f"http://{XSSBOT_HOST}"


class XSSBotException(Exception):
    pass


class InvalidRequestError(XSSBotException):
    def __init__(self, response: Any):
        self.response = response
        super().__init__(f"Invalid request sent to XSSBot.")


class Cookie(TypedDict):
    name: str
    value: str
    domain: str
    path: NotRequired[str]
    sameSite: NotRequired[Literal["Strict", "Lax", "None"]]
    httpOnly: NotRequired[bool]
    secure: NotRequired[bool]


def visit(
    url: str,
    cookies: list[Cookie],
    spoof_mtls=True,
    timeout: Optional[int] = None,
    network_timeout: Optional[int] = None,
):
    username = get_username()
    if spoof_mtls and username is not None:
        mtls_user = {"username": username, "isStaff": is_staff()}
    else:
        mtls_user = None

    data = {"url": url, "cookies": cookies}

    if timeout:
        data["timeout"] = timeout

    if network_timeout:
        data["networkTimeout"] = network_timeout

    if mtls_user:
        data["mtlsUser"] = mtls_user

    r = requests.post(
        f"{XSSBOT_URL}/visit",
        headers={
            "User-Agent": "pyquocca",
        },
        json=data,
    )

    if r.status_code == 204:
        return
    elif r.status_code == 400:
        raise InvalidRequestError(r.json())
    else:
        raise XSSBotException(r.content)
