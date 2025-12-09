"""
aioz.truongle - Apr 5, 2023
dody parse
"""
import logging
from fastapi import Request, File
from typing import Union, List
from json import JSONDecodeError
from ..common.errors import BadRequest
from starlette.datastructures import FormData

logger = logging.getLogger("app.com.bodyParse")


async def parse_form(reqs_form: FormData):
    payload = {}
    for k in reqs_form.keys():
        if len(reqs_form.getlist(k)) > 1:
            payload[k] = reqs_form.getlist(k)
        else:
            payload[k] = reqs_form.get(k)
    return payload


async def body_parse(request: Request) -> dict:
    content_type = request.headers.get('Content-Type')
    if content_type is None:
        raise BadRequest(message='No Content-Type provided!')
    # get JSON
    elif content_type in ['application/json', 'text/plain']:
        # logger.debug("Request with JSON")
        try:
            payload = await request.json()
            return payload
        except JSONDecodeError as e:
            logger.error(f"Invalid JSON data: {str(e)}")
            raise BadRequest(message='Invalid JSON data')

    # get FORM
    elif (content_type == 'application/x-www-form-urlencoded' or
          content_type.startswith('multipart/form-data')):
        # logger.debug("Request with form")
        try:
            reqs_form = await request.form()
            payload = await parse_form(reqs_form)
            return payload
        except Exception as e:
            logger.error(f"Invalid Form data: {str(e)}")
            raise BadRequest(message='Invalid Form data')
    else:
        raise BadRequest(message='Content-Type not supported!')
