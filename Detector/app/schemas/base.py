"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
request and response schemas
"""
import os
from pydantic import BaseModel
from typing import Union, List, Any, Optional


class BaseResp(BaseModel):
    status_code: int = 200
    success: bool = True


class BasePagination(BaseModel):
    total: int
    pages: int
    page: int
    page_size: int


class AppCfg(BaseModel):
    data_dir: Optional[str] = os.path.join(os.getcwd(), "data")
    cache_dir: Optional[str] = os.path.join(os.getcwd(), ".cache")