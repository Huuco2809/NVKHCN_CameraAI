"""
aioz.truongle - Mar 29, 2023
"""
import uuid
import logging
from app.common import JWT
from app.common import errors as app_errors

logger = logging.getLogger("app.common.auth")


def get_token(
        payload: dict,
        payload_blacklist=None
) -> str:
    if payload_blacklist is None:
        payload_blacklist = {}

    for k, v in payload_blacklist.items():
        payload.pop(k, None)

    token = JWT.create_token(payload)
    return token


def verify_token(token: str) -> [bool, dict]:
    token = token.split(" ")[-1]
    payload, check = JWT.check_token(token)
    return check, payload


