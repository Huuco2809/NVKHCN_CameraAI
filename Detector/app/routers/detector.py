"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
detector router
"""
import logging
from .. import schemas
from ..controllers import detector
from fastapi import APIRouter, Depends
from fastapi.security import APIKeyHeader


logger = logging.getLogger("app.router.detector")

router = APIRouter(prefix="",
                   tags=["Detector"],
                   dependencies=[Depends(APIKeyHeader(name="x-api-key"))],
                   responses={
                         400: {"model": schemas.ExceptionErrors},
                         422: {"model": schemas.CustomValidationErrors}
                     },
                   )

router.add_api_route("/detect",
                     endpoint=detector.detector,
                     methods=['POST'],
                     responses={
                         200: {"model": schemas.DetectResp},
                     },
                     openapi_extra={
                         "requestBody": {
                             "content": {"multipart/form-data": {"schema": schemas.DetectReqs.schema()}},
                             "required": True},
                     },
                     )