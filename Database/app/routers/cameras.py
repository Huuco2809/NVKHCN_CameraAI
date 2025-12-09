"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
detector router
"""
from .. import schemas
from ..controllers import cameras
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer


router = APIRouter(prefix="/cameras",
                   tags=["Cameras"],
                   dependencies=[Depends(HTTPBearer())],
                   responses={
                         400: {"model": schemas.ExceptionErrors},
                         422: {"model": schemas.CustomValidationErrors}
                     },
                   )

router.add_api_route("",
                     endpoint=cameras.get_cameras_info_paging,
                     methods=['GET'],
                     responses={
                         200: {"model": schemas.GetCamsInfoPagingResp},
                     },
                     )


router.add_api_route("/{camera_id}",
                     endpoint=cameras.get_camera_info,
                     methods=['GET'],
                     responses={
                         200: {"model": schemas.GetCamInfoResp},
                     },
                     )

router.add_api_route("/{camera_id}",
                     endpoint=cameras.update_camera_info,
                     methods=['PUT'],
                     responses={
                         200: {"model": schemas.UpdateResp},
                     },
                     openapi_extra={
                         "requestBody": {
                             "content": {"application/json": {"schema": schemas.UpdateCamInfoReqs.schema()}},
                             "required": True}
                     },
                     )

