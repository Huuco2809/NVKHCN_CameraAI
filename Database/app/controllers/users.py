"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
user
"""
import re
import logging
import hashlib
from .. import DbManage, DBCollections
from .. import schemas
from ..common.auth import get_token, verify_token
from ..common.body_parser import body_parse
from ..common.errors import (
    BadRequest,
    AuthorizationFailed,
    InternalServerError
)
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

logger = logging.getLogger("app.ctl.user")


SECURITY = HTTPBearer(auto_error=False)

PW_FMT = "Password should have at least one number, one uppercase, one lowercase character, one special symbol." \
         " Should have at least 6 characters."
CHECK_PW = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@$!%*#?&])[A-Za-z0-9@$!#%*?&]{6,}$")

HASH_ALG = getattr(hashlib, "sha3_256")


def hashing(pw: str):
    return HASH_ALG(pw.encode()).hexdigest()


async def login(reqs: Request):
    # get body
    reqs_payload = await body_parse(reqs)
    reqs_payload = schemas.UserLoginReqs.parse_obj(reqs_payload)  # validate reqs

    user_info = await DbManage.query(DBCollections.USERS.value, {"username": reqs_payload.username})
    if len(user_info) == 0:
        raise BadRequest(message="Username not exists")

    # Evn@2023: 424918a4bf008d79342998cf9d308aae48f64d78110700290d370777df7f3280
    pw_hash = hashing(reqs_payload.password)
    if user_info[0].get("password") != pw_hash:
        raise AuthorizationFailed()

    token = get_token(payload={"username": reqs_payload.username})
    token = f"{SECURITY.model.scheme} {token}"
    resp = schemas.UserLoginResp(token=token)
    return JSONResponse(
        status_code=resp.status_code,
        content=resp.dict()
    )


async def change_password(reqs: Request):
    # get body
    reqs_payload = await body_parse(reqs)
    reqs_payload = schemas.UserChangePasswordReqs.parse_obj(reqs_payload)  # validate reqs

    # get username from token
    sec = await SECURITY(reqs)
    _, payload = verify_token(token=sec.credentials)
    username = payload["username"]

    user_info = await DbManage.query(DBCollections.USERS.value, {"username": username})
    old_pw_hash = hashing(reqs_payload.old_password)
    if old_pw_hash != user_info[0].get("password"):
        raise BadRequest(message="Old password is wrong")

    if not bool(CHECK_PW.match(reqs_payload.new_password)):
        raise BadRequest(message=PW_FMT)

    r = await DbManage.update(DBCollections.USERS.value,
                              query={"username": username},
                              new_value={"password": hashing(reqs_payload.new_password)}
                              )
    if r < 0:  # update failed
        raise InternalServerError()

    resp = schemas.UserChangePasswordResp()
    return JSONResponse(
        status_code=resp.status_code,
        content=resp.dict()
    )


async def get_profile(reqs: Request):
    sec = await SECURITY(reqs)
    _, payload = verify_token(token=sec.credentials)
    resp = schemas.UserProfileResp(user=payload)
    return JSONResponse(
        status_code=resp.status_code,
        content=resp.dict()
    )
