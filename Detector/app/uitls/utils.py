"""
aioz.aiar.truongle - Oct 19, 2022
api utils
"""
import io
import os
import uuid
import enum
import logging
from PIL import Image
from urllib.parse import urlparse
from typing import Union, Dict, List
from fastapi.responses import Response

logger = logging.getLogger("apps.utl.utl")


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


def upload_s3(img_pth, media_dir, s3_manage=None):
    if s3_manage is None:
        logger.info(f"saved file at {img_pth}")
        return img_pth.replace(media_dir, "").strip("/")
    else:
        obj_url = s3_manage.upload_file(
            file_name=img_pth,
            object_name=img_pth.replace(media_dir, "").strip("/"),
        )
        os.remove(img_pth)
        return obj_url


def get_file_path(write_dir: str,
                  name: str, prefix: str, ext: str,
                  override: bool = False):
    img_pth = os.path.join(write_dir, f"{name}{prefix}{ext}")
    if not override:
        count = 0
        while os.path.exists(img_pth):
            img_pth = os.path.join(write_dir, f"{name}{prefix}_{count}{ext}")
            count += 1
            if count == 100:
                logger.error(f"{img_pth} can not write")
                return ""
    return img_pth


def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except:
        return False


def write_file(file: Union[str, bytes],
               name: str,
               media_dir: str,
               sub_dir: Union[List[str], str] = "",
               prefix: str = "",
               override: bool = False,
               get_full_path: bool = False,
               s3_manage=None, **kwargs):
    if isinstance(sub_dir, str):
        sub_dir = [sub_dir]
    write_dir = os.path.join(media_dir, "/".join(sub_dir))

    if uri_validator(file):
        return file

    elif isinstance(file, bytes):
        os.makedirs(write_dir, exist_ok=True)
        ext = kwargs.get("ext", "jpg")
        img_pth = get_file_path(write_dir, name, prefix, ext, override)
        # save
        with open(img_pth, "wb") as f:
            f.write(file)
        # im_url = upload_s3(img_pth, media_dir, s3_manage)
        return img_pth if get_full_path else img_pth.replace(media_dir, "").strip("/")
    else:
        logger.debug("file is none, or invalid")
        return None


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
