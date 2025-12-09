"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
user
"""
import logging
from .. import (
    schemas,
    DbManage, DBCollections,
    get_media_url
)
from typing import List, Dict
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.ctl.frames")


async def get_objects_latestNFrame(n: int = 10) -> List[Dict]:
    pipeline = [
        {"$group": {
            "_id": "$camera_id",
            "objects": {
                "$topN": {"n": n, "sortBy": {"_id": -1}, "output": "$objects"}}
        },
        }
    ]
    _res = await DbManage.aggregate(DBCollections.FRAMES.value, pipeline=pipeline)
    res = []
    for r in _res:
        for f_obj in r["objects"]:
            for obj in f_obj:
                if not obj["in_area"]:
                    continue
                if obj["thumbnail"] == "":
                    continue
                obj["thumbnail"] = await get_media_url(obj["thumbnail"])
                obj = schemas.DetObjetResp(camera_id=r["_id"], **obj)
                res.append(obj.dict())
    return res


async def get_objects_as_list() -> List[Dict]:
    lookup = {
        "from": DBCollections.FRAMES.value,
        "let": {"frame_cam_id": "$camera_id"},
        "pipeline": [
            {"$match": {"$expr": {"$eq": ["$camera_id", "$$frame_cam_id"]}}},
            {"$sort": {"_id": -1}},
            {"$limit": 1},
        ],
        "as": "frame_objects",
    }

    pipeline = [
        {"$match": {"have_object": True}},
        {"$lookup": lookup},
    ]
    _res = await DbManage.aggregate(DBCollections.CAMERAS.value, pipeline=pipeline)
    res = []
    for r in _res:
        for f_obj in r["frame_objects"]:
            for obj in f_obj["objects"]:
                if not obj["in_area"]:
                    continue
                if obj["thumbnail"] == "":
                    continue
                obj["thumbnail"] = await get_media_url(obj["thumbnail"])
                obj = schemas.DetObjetResp(camera_id=r["camera_id"], camera_name=r["camera_name"], **obj)
                res.append(obj.dict())

    return res


async def get_objects_group_by_cam_id() -> Dict:
    lookup = {
        "from": DBCollections.FRAMES.value,
        "let": {"frame_cam_id": "$camera_id"},
        "pipeline": [
            {"$match": {"$expr": {"$eq": ["$camera_id", "$$frame_cam_id"]}}},
            {"$sort": {"_id": -1}},
            {"$limit": 1},
        ],
        "as": "frame_objects",
    }

    pipeline = [
        {"$match": {"have_object": True}},
        {"$lookup": lookup},
    ]
    _res = await DbManage.aggregate(DBCollections.CAMERAS.value, pipeline=pipeline)
    res = {}
    for r in _res:
        camera_id = r["camera_id"]
        if camera_id not in res.keys():
            res[camera_id] = []   # init list

        for f_obj in r["frame_objects"]:
            for obj in f_obj["objects"]:
                if not obj["in_area"]:
                    continue
                if obj["thumbnail"] == "":
                    continue
                obj["thumbnail"] = await get_media_url(obj["thumbnail"])
                obj = schemas.DetObjetResp(camera_id=r["camera_id"], camera_name=r["camera_name"], **obj)
                _obj = obj.dict()
                _obj["example"] = "example variable"
                res[camera_id].append(_obj)

    # logger.debug(f"res obj group cid: {res}")
    return res

async def get_objects():
    res = await get_objects_as_list()
    resp = schemas.GetObjectsResp(data=res)
    return JSONResponse(
        status_code=resp.status_code,
        content=resp.dict()
    )
