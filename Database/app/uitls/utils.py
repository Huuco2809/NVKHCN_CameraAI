"""
aioz.truongle - April 12
utils
"""
import os
import io
import enum
import uuid
import logging
from PIL import Image
from typing import Union, Dict, List
from fastapi.responses import Response


logger = logging.getLogger("app.util.util")


class MIMETYPE(enum.Enum):
    AUDIO_WAV = "audio/wav"
    IMAGE_JPG = "image/jpeg"
    IMAGE_PNG = "image/png"
    JSON = "application/json"
    WEBM_VID = "video/webm"
    WEBM_AUD = "audio/webm"


def get_uuid():
    return uuid.uuid4().hex


def serve_image(
        status_code: int,
        image: Union[bytes, Image.Image, str],
        mimetype: str = MIMETYPE.IMAGE_PNG.value,
        custom_header: Dict = None
):
    custom_header = {} if custom_header is None else custom_header
    if isinstance(image, str) and os.path.isfile(image):
        pil_im = Image.open(image)
    elif isinstance(image, (Image.Image, bytes)):
        pil_im = image
    else:
        logger.error(f"un support image type: {type(image)}")
        raise Exception

    buff = io.BytesIO()
    if mimetype == MIMETYPE.IMAGE_PNG.value:
        pil_im.save(buff, 'PNG')
    else:
        pil_im.save(buff, 'JPEG')
    buff.seek(0)

    return Response(
        status_code=status_code,
        content=buff.getvalue(),
        media_type=mimetype, headers=custom_header
    )


def str2bool(v):
    """
    https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise logger.error("boolean value expected")
