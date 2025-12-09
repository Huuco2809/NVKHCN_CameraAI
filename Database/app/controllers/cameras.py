"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
user
"""
import json
import logging
from .. import (
    schemas, mask_utils,
    DbManage, DBCollections,
    get_cam_socket_url, get_media_url
)
from ..common.body_parser import body_parse
from ..common.errors import (
    BadRequest,
    NotFound,
    InternalServerError
)
from typing import Optional, List, Dict, Literal
from fastapi.responses import JSONResponse
from fastapi import Request, Query

logger = logging.getLogger("app.ctl.cams")


async def post_process_cam_info(cam_info):
    cam_info["thumbnail"] = await get_media_url(cam_info["thumbnail"])
    cam_info["socket_url"] = await get_cam_socket_url(cam_info["camera_id"])
    return cam_info


async def get_list_camera_info(showing: bool = None, have_object: bool = None,
                               exclude_field: List = [],
                               ) -> List[Dict]:
    match = {}
    if showing is not None:
        match["showing"] = showing
    if have_object is not None:
        match["have_object"] = have_object
    pipeline = [{"$match": match}]
    res = await DbManage.aggregate(DBCollections.CAMERAS.value, pipeline=pipeline)
    # process:
    data = []
    for r in res:
        r = await post_process_cam_info(r)
        data.append(schemas.CamInfo(**r).dict(exclude={ex for ex in exclude_field}))
    return data


async def get_cameras_info(
        showing: Optional[bool] = Query(default=None),
        have_object: Optional[bool] = Query(default=None)
):
    data = await get_list_camera_info(showing, have_object)
    resp = schemas.GetCamsInfoResp(data=data)
    return JSONResponse(
        status_code=resp.status_code,
        content=resp.dict()
    )


async def get_cameras_info_paging(
        showing: Optional[bool] = Query(default=None),
        have_object: Optional[bool] = Query(default=None),
        sort: Literal["latest", "earliest"] = Query(default="latest"),
        page_size: Optional[int] = Query(default=50, ge=1, le=100),
        page: Optional[int] = Query(default=1, gt=0)
):

    sort_order = -1 if sort == "latest" else 1
    match = {}
    if showing is not None:
        match["showing"] = showing
    if have_object is not None:
        match["have_object"] = have_object

    logger.debug(f"Query params: sort - {sort}, page_size - {page_size}, page - {page} ")
    res = await DbManage.pagination(
        coll_name=DBCollections.CAMERAS.value,
        match=match,
        sort=sort_order, page=page, page_size=page_size,
    )

    logger.debug(f"num data: {len(res)}")
    if len(res) == 0:
        raise InternalServerError(message="No data found on request")

    items = []
    for r in res[0]["items"]:
        r = await post_process_cam_info(r)
        items.append(schemas.CamInfo(**r).dict())

    resp_data = schemas.CamsInfoPagination(
        total=res[0]["total"],
        pages=res[0]["pages"],
        page=res[0]["page"],
        page_size=res[0]["page_size"],
        items=items
    )
    resp = schemas.GetCamsInfoPagingResp(
        data=resp_data
    )

    return JSONResponse(
        status_code=resp.status_code,
        content=json.loads(resp.json())  # fix type for JSON serialization
    )


async def get_camera_info(camera_id: str):
    res = await DbManage.query(DBCollections.CAMERAS.value, {"camera_id": camera_id})
    if len(res) == 0:
        raise NotFound()
    res = await post_process_cam_info(res[0])
    resp = schemas.GetCamInfoResp(data=res)
    return JSONResponse(
        status_code=resp.status_code,
        content=resp.dict()
    )


async def update_camera_info(camera_id: str, reqs: Request):
    reqs_payload = await body_parse(reqs)
    reqs_payload = schemas.UpdateCamInfoReqs.parse_obj(reqs_payload)  # validate reqs

    cam_info = await DbManage.query(DBCollections.CAMERAS.value, {"camera_id": camera_id})
    if len(cam_info) == 0:
        raise BadRequest(message="Camera_id not exists")

    up_doc = reqs_payload.dict(exclude_none=True)
    regions = reqs_payload.regions
    if regions is not None:
        if len(regions) > 0:
            mask_path = cam_info[0]["thumbnail"].replace("_thumbnail.jpg", "_mask.jpg")
            mask_utils.create_mask(polygons=regions, mask_pth=mask_path,
                                   image_width=cam_info[0]["cam_width"], image_height=cam_info[0]["cam_height"])
        else:
            mask_path = ""
        up_doc["mask"] = mask_path

    if len(up_doc.keys()) > 0:
        res = await DbManage.update(DBCollections.CAMERAS.value,
                                    query={"camera_id": camera_id},
                                    new_value=up_doc)
        if res == -1:
            raise InternalServerError()

    resp = schemas.UpdateResp()
    return JSONResponse(
        status_code=resp.status_code,
        content=resp.dict()
    )
