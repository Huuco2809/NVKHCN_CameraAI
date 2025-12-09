"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
request and response schemas
"""
from .base import BaseResp
from pydantic import BaseModel
from typing import Union, List, Any, Optional


class DetObject(BaseModel):
    cls_name: str
    thumbnail: str


class DetObjetResp(BaseModel):
    camera_id: str
    camera_name: Optional[str] = ""
    cls_name: str
    thumbnail: str
    in_area: bool
    go_in: bool
    go_out: bool
    position: Optional[str] = ""


class GetObjectsResp(BaseResp):
    data: List[DetObjetResp]






