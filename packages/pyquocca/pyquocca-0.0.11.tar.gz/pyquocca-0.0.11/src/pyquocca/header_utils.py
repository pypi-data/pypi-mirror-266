from typing import Optional

from flask import Request
from flask import request as flask_request

USERNAME_HEADER = "X-mTLS-Username"
STAFF_HEADER = "X-mTLS-Staff"
FIRST_NAME_HEADER = "X-mTLS-First-Name"
LAST_NAME_HEADER = "X-mTLS-Last-Name"
FULL_NAME_HEADER = "X-mTLS-Full-Name"
IMPERSONATED_BY_HEADER = "X-mTLS-Impersonated-By"

# Would be nice to have a system to differentiate bots from regular staff.
# Maybe a third CA?
XSSBOT_USERNAME = "XSSBot"


def get_username(request: Optional[Request] = None) -> Optional[str]:
    """Returns the username from the current request."""
    r = request if request is not None else flask_request
    return r.headers.get(USERNAME_HEADER, None)


def get_impersonator(request: Optional[Request] = None) -> Optional[str]:
    """A user may be being impersonated by a staff user. This functions return the impersonator's username."""
    r = request if request is not None else flask_request
    return r.headers.get(IMPERSONATED_BY_HEADER, None)


def is_staff(request: Optional[Request] = None) -> bool:
    """Returns whether or not the request being made is made by a staff user."""
    r = request if request is not None else flask_request
    return r.headers.get(STAFF_HEADER, "false") == "true"


def is_xssbot(request: Optional[Request] = None) -> bool:
    """Determines if the current request is being made by XSSBot, either directly or via impersonation."""
    r = request if request is not None else flask_request
    return (is_staff(r) and get_username(r) == XSSBOT_USERNAME) or (
        get_impersonator() == XSSBOT_USERNAME
    )


def get_first_name(request: Optional[Request] = None) -> Optional[str]:
    """Returns the first name of the current user if available, then falls back to username."""
    r = request if request is not None else flask_request
    return r.headers.get(FIRST_NAME_HEADER, get_username(request))


def get_last_name(request: Optional[Request] = None) -> Optional[str]:
    """Returns the last name of the current user if available, then falls back to username."""
    r = request if request is not None else flask_request
    return r.headers.get(LAST_NAME_HEADER, get_username(request))


def get_full_name(request: Optional[Request] = None) -> Optional[str]:
    """Returns the full name of the current user if available, then falls back to username."""
    r = request if request is not None else flask_request
    return r.headers.get(FULL_NAME_HEADER, get_username(request))
