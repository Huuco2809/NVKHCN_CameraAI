"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
media router
"""
from .. import schemas
from ..controllers import media
from fastapi import APIRouter


router = APIRouter(prefix="/media",
                   tags=["Media"],
                   responses={
                         400: {"model": schemas.ExceptionErrors},
                         422: {"model": schemas.CustomValidationErrors}
                     },
                   )

router.add_api_route("/{file_path:path}",
                     endpoint=media.get_file,
                     include_in_schema=False,
                     methods=['GET'],
                     responses={
                         200: {"content": {"image/png": {}}},
                     },
                     )