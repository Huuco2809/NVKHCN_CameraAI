"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
detector router
"""
from .. import schemas
from ..controllers import users
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

router = APIRouter(prefix="/users",
                   tags=["User"],
                   # dependencies=[Depends(HTTPBearer())],
                   responses={
                         400: {"model": schemas.ExceptionErrors},
                         422: {"model": schemas.CustomValidationErrors}
                     },
                   )

router.add_api_route("/login",
                     endpoint=users.login,
                     methods=['POST'],
                     responses={
                         200: {"model": schemas.UserLoginResp},
                     },
                     openapi_extra={
                         "requestBody": {
                             "content": {"application/json": {"schema": schemas.UserLoginReqs.schema()}},
                             "required": True},
                     },
                     )


router.add_api_route("/change-password",
                     endpoint=users.change_password,
                     methods=['POST'],
                     dependencies=[Depends(HTTPBearer())],
                     responses={
                         200: {"model": schemas.UserProfileResp},
                     },
                     openapi_extra={
                         "requestBody": {
                             "content": {"application/json": {"schema": schemas.UserChangePasswordReqs.schema()}},
                             "required": True},
                     },
                     )


router.add_api_route("/profile",
                     endpoint=users.get_profile,
                     methods=['GET'],
                     dependencies=[Depends(HTTPBearer())],
                     responses={
                         200: {"model": schemas.UserProfileResp},
                     },
                     )

