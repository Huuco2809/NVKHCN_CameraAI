"""
aioz.truongle - Mar 29, 2023
dependencies
"""
import os
import logging
from jose import jwt
from typing import Dict
from fastapi import Request
from .. import ArtDbManage
from .body_parser import body_parse
from ..utils.utils import ARTWORK_DB_COLL
from ..common.errors import AuthorizationFailed

logger = logging.getLogger("app.ver2.cm.depend")


def get_token_payload(token: str) -> Dict:
    token = token.split(" ")[-1]
    payload = jwt.decode(token, key=None, options={"verify_signature": False})
    return payload


async def verify_uuid(reqs: Request) -> bool:
    token = reqs.headers.get("Authorization")
    body_payload = await body_parse(reqs)
    uuid = reqs.path_params.get("uuid") or body_payload.get("uuid") or reqs.query_params.get("uuid")
    # check if Uuid and Token match
    token_payload = get_token_payload(token=token)
    res, e = ArtDbManage.query(ARTWORK_DB_COLL.USER_ACCOUNT.value, query={"uuid": uuid})
    if len(res) > 0:
        if res[0]["wallet_address"] != token_payload["wallet_address"]:
            logger.warning(f"token wallet: {token_payload['wallet_address']} - reqs wallet: {res[0]['wallet_address']}")
            raise AuthorizationFailed()
    return True
