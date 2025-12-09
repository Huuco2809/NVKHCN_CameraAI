"""
aioz.truongle - Apr 3, 2023
request and response schemas
"""
from pydantic import BaseModel
from typing import Union, List, Any


class BaseResp(BaseModel):
    status_code: int = 200
    success: bool = True


class BasePagination(BaseModel):
    total: int
    pages: int
    page: int
    page_size: int
