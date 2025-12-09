"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
detector
"""
import os
import cv2
import io
import json
import asyncio
import time
import logging
import numpy as np
from PIL import Image
from .. import schemas
from .. import detApi
from ..common.body_parser import body_parse
from ..common.errors import (
    InternalServerError,
    BadRequest,
)
from fastapi import status, Request
from fastapi.responses import JSONResponse
from starlette.datastructures import UploadFile

logger = logging.getLogger("app.ctl.detector")


async def api_proceed(reqs_payload: schemas.DetectReqs, **kwargs):
    res, e = detApi.proceed(
        input_data=reqs_payload.file,
    )
    if len(e) > 0:  # retrieval process failed
        raise InternalServerError(detail=e)
    return res


async def detector(reqs: Request):
    tic = time.perf_counter()
    # get body
    reqs_payload = await body_parse(reqs)
    reqs_payload = schemas.DetectReqs.parse_obj(reqs_payload)  # validate reqs

    file = reqs_payload.file
    if isinstance(file, UploadFile):
        bfile = await file.read()
        im_data = cv2.imdecode(np.frombuffer(bfile, np.uint8), 1)
        im_data = im_data[:, :, ::-1]  # BGR 2 RGB
        # im_data = Image.open(io.BytesIO(bfile))
        reqs_payload.file = im_data

    res = await api_proceed(reqs_payload)

    rets_data = []
    for r in res:
        rets_data.append(schemas.ObjectInfo(box=r.box, cls_id=r.cls_id, cls_name=r.cls_name, conf=r.conf))

    resp = schemas.DetectResp(data=rets_data)
    # resp = resp.dict()
    # resp["time"] = str((time.perf_counter() - tic)*1000)
    # return resp
    return JSONResponse(
        status_code=resp.status_code,
        content=json.loads(resp.json())
    )
