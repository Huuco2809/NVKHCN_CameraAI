"""
manh.truongle  - Nov 23, 2021
truonnglm.spk@gmail.com
define some model of database
"""
import os
import datetime
from pydantic import BaseModel, validator
from typing import Optional, Union, List, Tuple


class UsersModel(BaseModel):
    username: str
    password: str


class CamerasModel(BaseModel):
    camera_id: str
    camera_name: str
    rtsp: str
    cam_width: int
    cam_height: int
    socket_url: Optional[str] = ""
    regions: Optional[List[List[Tuple[int, int]]]] = []
    showing: Optional[bool] = False
    visualize: Optional[bool] = True
    have_object: Optional[bool] = False
    tracking: Optional[bool] = True
    thumbnail: Optional[str] = ""
    mask: Optional[str] = ""

    @validator("thumbnail", "mask", pre=True)
    def validate_atts(cls, v, values, field):
        if field.name == "mask":
            return os.path.relpath(v) if len(v) > 0 else ""
        else:
            return os.path.relpath(v) if len(v) > 0 else ""


class DetObject(BaseModel):
    box: List[int]
    cls_name: str
    cls_id: int
    conf: float
    thumbnail: Optional[str] = ""
    obj_id: Optional[int] = -1
    in_area: Optional[bool] = False
    go_in: Optional[bool] = False
    go_out: Optional[bool] = False
    position: Optional[str] = ""
    

    @validator("thumbnail", pre=True)
    def validate_atts(cls, v, values, field):
        if field.name == "thumbnail":
            return os.path.relpath(v) if len(v) > 0 else ""


class FramesModel(BaseModel):
    camera_id: str
    thumbnail: str
    create_date: datetime.datetime
    objects: Optional[List[DetObject]] = []
    have_object: Optional[bool] = False
    in_area: Optional[int] = 0
    go_in: Optional[int] = 0
    go_out: Optional[int] = 0

    @validator("thumbnail", pre=True)
    def validate_atts(cls, v, values, field):
        if field.name == "thumbnail":
            return os.path.relpath(v) if len(v) > 0 else ""
