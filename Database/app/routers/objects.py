"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
detector router
"""
from .. import schemas
from ..controllers import objects
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer


router = APIRouter(prefix="/objects",
                   tags=["Objects"],
                   dependencies=[Depends(HTTPBearer())],
                   responses={
                         400: {"model": schemas.ExceptionErrors},
                         422: {"model": schemas.CustomValidationErrors}
                     },
                   )

router.add_api_route("/objects-in-area",
                     endpoint=objects.get_objects,
                     methods=['GET'],
                     responses={
                         200: {"model": schemas.GetObjectsResp},
                     },
                     )
