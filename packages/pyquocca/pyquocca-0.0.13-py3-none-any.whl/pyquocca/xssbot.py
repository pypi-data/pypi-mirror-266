import os
from typing import Any, Literal, Optional

import requests
from typing_extensions import NotRequired, TypedDict

from .header_utils import get_username, is_staff

XSSBOT_URL = os.getenv("XSSBOT_URL")


class XSSBotException(Exception):
    pass


class MissingURLError(XSSBotException):
    def __init__(self):
        super().__init__(
            f"Missing XSSBOT_URL environment variable for accessing XSSBot."
        )


class BadRequestError(XSSBotException):
    def __init__(self, response: Any):
        self.response = response
        super().__init__(f"XSSBot returned a 400 Bad Request response: {response!r}")


class Cookie(TypedDict):
    name: str
    value: str
    domain: str
    path: NotRequired[str]
    sameSite: NotRequired[Literal["Strict", "Lax", "None"]]
    httpOnly: NotRequired[bool]
    secure: NotRequired[bool]


class Options(TypedDict):
    userAgent: NotRequired[str]
    mtlsDomains: NotRequired[list[str]]


def visit(
    url: str,
    /,
    cookies: list[Cookie],
    *,
    spoof_mtls=True,
    timeout: Optional[int] = None,
    network_timeout: Optional[int] = None,
    options: Options = {},
):
    """Tells XSSBot to visit a page using a headless browser to check if a user's XSS payload has worked.

    :param url: URL of site/page to visit
    :type url: str
    :param cookies: list of cookies to set for the visit
    :type cookies: list[Cookie]
    :param spoof_mtls: sets whether or not the current user's mTLS identity will be spoofed if available, defaults to True
    :type spoof_mtls: bool, optional
    :param timeout: sets the timeout for the entire visit, default is decided by XSSBot
    :type timeout: Optional[int], optional
    :param network_timeout: sets the timeout for network calls, default is decided by XSSBot
    :type network_timeout: Optional[int], optional
    :raises MissingURLError: if the XSSBOT_URL environment variable isn't set
    :raises BadRequestError: if XSSBot responds with a 400 Bad Request error
    :raises XSSBotException: if XSSBot responds with any other non-200 response code
    """
    if XSSBOT_URL is None:
        raise MissingURLError()

    username = get_username()
    if spoof_mtls and username is not None:
        mtls_user = {"username": username, "isStaff": is_staff()}
    else:
        mtls_user = None

    data = {"url": url, "cookies": cookies, **options}

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
        raise BadRequestError(r.json())
    else:
        raise XSSBotException(r.content)
