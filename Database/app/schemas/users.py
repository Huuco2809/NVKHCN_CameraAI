"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
request and response schemas
"""
from .base import BaseResp
from pydantic import BaseModel
from typing import Union, List, Any, Optional, Dict


class UserLoginReqs(BaseModel):
    username: str
    password: str


class UserLoginResp(BaseResp):
    token: Optional[str] = ""


class UserChangePasswordReqs(BaseModel):
    old_password: str
    new_password: str


class UserChangePasswordResp(BaseResp):
    success = True


class UserProfile(BaseModel):
    username: str


class UserProfileResp(BaseResp):
    user: UserProfile

