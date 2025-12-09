"""
aioz.truongle - Mar 29, 2023
"""
import json
import logging
import pydantic
from .. import schemas
from .auth import verify_token
from .errors import (
    AppErrors,
    InternalServerError,
    AuthorizationFailed
)
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
    logger.error(f"Err at {request.scope['path']} {request.scope.get('endpoint')} {exc}")
    if isinstance(exc, pydantic.error_wrappers.ValidationError):
        return await validation_exc(exc, request)

    elif isinstance(exc, AppErrors):
        return JSONResponse(
            status_code=exc.err_msg.status_code,
            content=exc.response(),
        )
    else:
        logger.error(exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            # content=InternalServerError(message=f"Something was wrong {str(exc)}").response()
            content=InternalServerError(message=f"Something was wrong").response()
        )


async def auth(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise AuthorizationFailed(message="Missing authorization method in the headers")
    verify, _ = verify_token(token)
    if verify:
        return True
    else:
        raise AuthorizationFailed()
