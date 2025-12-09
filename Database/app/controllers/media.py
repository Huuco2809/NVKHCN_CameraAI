"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
user
"""
import os
import logging
from .. import AppCfg
from ..uitls import utils as api_utils
from fastapi import status

logger = logging.getLogger("app.ctl.media")


async def get_file(file_path: str):
    # get body
    image = os.path.join(AppCfg["media_dir"], file_path)
    return api_utils.serve_image(
        status_code=status.HTTP_200_OK,
        image=image,
        mimetype=api_utils.MIMETYPE.IMAGE_JPG.value
    )

