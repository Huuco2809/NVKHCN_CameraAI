"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
request and response schemas
"""
import numpy as np
from .base import BaseResp, BasePagination
from pydantic import BaseModel, validator
from typing import Union, List, Any, Optional, Tuple


class CamInfo(BaseModel):
    camera_id: str
    camera_name: str
    rtsp: str
    thumbnail: str
    socket_url: str
    showing: bool
    have_object: bool
    tracking: bool
    regions: List[List[Tuple[int, int]]]


class GetCamsInfoResp(BaseResp):
    data: List[CamInfo]


class CamsInfoPagination(BasePagination):
    items: List[CamInfo]


class GetCamsInfoPagingResp(BaseResp):
    data: CamsInfoPagination


class GetCamInfoResp(BaseResp):
    data: CamInfo


class UpdateCamInfoReqs(BaseModel):
    showing: Optional[bool]
    regions: Optional[List[List[Tuple[int, int]]]]
    tracking: Optional[bool]
    visualize: Optional[bool]

    @validator("regions", pre=True)
    def validate_atts(cls, v, values, field):
        if field.name == "regions":
            _v = []
            for l in v:
                l = np.asarray(l).astype(int).tolist()
                _v.append(l)
            return _v


class UpdateResp(BaseResp):
    message = "Updated successfully"




