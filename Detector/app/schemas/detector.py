"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
schemas
"""
from .base import BaseResp
from pydantic import BaseModel, validator
from fastapi import status, File, UploadFile
from typing import Union, List, Any, Optional


class ObjectInfo(BaseModel):
    box: List[int]
    conf: float
    cls_name: str
    cls_id: int

    @validator("box", "conf", pre=True)
    def validate_atts(cls, v, values, field):
        if field.name == "box":
            return [int(_v) for _v in v]
        else:
            return round(v, 5)


class DetectReqs(BaseModel):
    file: UploadFile


class DetectResp(BaseResp):
    data: List[ObjectInfo]