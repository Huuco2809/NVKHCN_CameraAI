"""
aioz.truongle - Mar 29, 2023
truonnglm.spk@gmail.com
"""
import json
import httpx
import logging
import pydantic
from .. import schemas
from .errors import (
    AppErrors,
    InternalServerError,
    AuthorizationFailed
)
from omegaconf import DictConfig
from fastapi import Request, status
from fastapi.responses import JSONResponse


logger = logging.getLogger("app.common.mid")


async def validation_exc(exc, request: Request):
    exc_json = json.loads(exc.json())
    valid_arr = schemas.CustomValidationErrors()

    for error in exc_json:
        valid_arr.message.append(error['loc'][-1] + f": {error['msg']}")
    return JSONResponse(
        status_code=valid_arr.status_code,
        content=valid_arr.dict()
    )


async def errors_handling(exc, request: Request, call_next):
    if isinstance(exc, pydantic.error_wrappers.ValidationError):
        return await validation_exc(exc, request)

    elif isinstance(exc, AppErrors):
        return JSONResponse(
            status_code=exc.err_msg.status_code,
            content=exc.response(),
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=InternalServerError(message=f"Something was wrong {str(exc)}").response()
        )


async def auth(request: Request, auth_server: DictConfig):
    url = f"{auth_server.host}:{auth_server.port}{auth_server.route}"
    async with httpx.AsyncClient() as client:
        headers = dict(request.headers)
        headers.pop("content-length", None)  # because send only header
        headers.pop("content-type", None)  # because send only header

        resp = await client.get(url, headers=headers)
        if resp.status_code == status.HTTP_200_OK:
            return True
        else:
            raise AuthorizationFailed(**resp.json())


async def verify_api_key(request: Request, api_key_path: str = None):
    x_api_key = request.headers.get("x-api-key")
    if not x_api_key:
        raise AuthorizationFailed(message="Missing field x-api-key in header")
    with open(api_key_path, 'r') as apikey:
        key = apikey.read().replace('\n', '')
    if x_api_key == key:
        return True
    else:
        raise AuthorizationFailed()
