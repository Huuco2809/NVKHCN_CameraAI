"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
request and response schemas
"""
from typing import Union, List
from pydantic import BaseModel


class ExceptionErrors(BaseModel):
    status_code: int = 400
    message: str


class CustomValidationErrors(BaseModel):
    status_code: int = 422
    message: List[str] = []
