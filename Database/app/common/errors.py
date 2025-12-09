"""
aioz.truongle - Mar 29, 2023
"""
import logging
from .. import schemas
from fastapi import status


class AppErrors(Exception):
    err_msg: schemas.ExceptionErrors

    def __init__(self, **kwargs):
        super(AppErrors, self).__init__()
        self.kwargs = kwargs

    def response(self):
        json_data = self.err_msg.dict()
        json_data.update(self.kwargs)
        return json_data


class InternalServerError(AppErrors):
    err_msg = schemas.ExceptionErrors(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Something was wrong"
    )


class BadRequest(AppErrors):
    err_msg = schemas.ExceptionErrors(
        status_code=status.HTTP_400_BAD_REQUEST,
        message="Bad request"
    )


class NotFound(AppErrors):
    err_msg = schemas.ExceptionErrors(
        status_code=status.HTTP_404_NOT_FOUND,
        message="Not found"
    )


class AuthorizationFailed(AppErrors):
    err_msg = schemas.ExceptionErrors(
        status_code=status.HTTP_401_UNAUTHORIZED,
        message="Authorization failed"
    )
