"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
user
"""
import io
import json
import asyncio
import logging
import time

from PIL import Image
from typing import Dict
from .. import (
    AppCfg,
    AppTemplates,
    DbManage, DBCollections,
    vis_utils
)
from ..controllers import objects, cameras
from fastapi import WebSocket, Request

logger = logging.getLogger("app.ctl.sockets")


async def read_image(frame_info: Dict) -> bytes:
    # logger.debug(f"read thumbnail: {image_path}")
    image_path = frame_info["thumbnail"]
    pil_im = Image.open(image_path)
    # logger.debug(f"in_area: {cam_info['in_erea']}, go_in: {cam_info['go_in']}, go_out {cam_info['go_out']}")
    if frame_info.get("visualize", True):
        # tic = time.perf_counter()
        pil_im = vis_utils.pil_draw_info(pil_im, frame_info["objects"], frame_info["regions"])
        # logger.debug(f"vis time: {time.perf_counter() - tic}")

    buff = io.BytesIO()
    pil_im.save(buff, 'jpeg')
    buff.seek(0)
    return buff.getvalue()


async def get_latest_frame(camera_id: str) -> bytes:
    pipeline = [
        {"$match": {"camera_id": camera_id}},
        {"$sort": {"_id": -1}},
        {"$limit": 1},
        {"$lookup": {
            "from": DBCollections.CAMERAS.value,
            "localField": "camera_id",
            "foreignField": "camera_id",
            "as": "camera_info",
        }},
        {"$set": {
            "visualize": {"$first": "$camera_info.visualize"},
            "regions": {"$first": "$camera_info.regions"},
        }},
        {"$project": {"camera_info": 0}}
    ]
    res = await DbManage.aggregate(DBCollections.FRAMES.value, pipeline=pipeline)
    # cam_info = await DbManage.query(DBCollections.CAMERAS.value, query={"camera_id": camera_id})
    if len(res) > 0:
        image = await read_image(res[0])
        return image
    else:
        # logger.warning(f"{camera_id} doesn't have any frame")
        return bytes()


async def stream_camera(ws: WebSocket, camera_id: str):
    await ws.accept()
    try:
        while True:
            image = await get_latest_frame(camera_id)
            await asyncio.sleep(0.01)
            await ws.send_bytes(image)
    except Exception as e:
        logger.error(f"Err at stream_camera: {e}")
    finally:
        await ws.close()


async def test_showing(request: Request, camera_id: str):
    server_url = AppCfg["server_address"]
    server_url = server_url.replace("http://", "ws://")
    ws_endpoint = f"{server_url}/ws/cameras-stream"
    return AppTemplates.TemplateResponse(
        "showImage.html",
        {"request": request, "camera_id": camera_id, "ws_endpoint": ws_endpoint})


async def get_objects(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await objects.get_objects_as_list()
            resp = json.loads(json.dumps({"data": data}))
            await asyncio.sleep(0.01)
            await ws.send_json(resp)
    except Exception as e:
        logger.error(f"Err at get_objects: {e}")
    finally:
        await ws.close()


async def test_get_objs_socket(request: Request):
    server_url = AppCfg["server_address"]
    server_url = server_url.replace("http://", "ws://")
    ws_endpoint = f"{server_url}/ws/objects-in-area"
    return AppTemplates.TemplateResponse(
        "showText.html",
        {"request": request, "ws_endpoint": ws_endpoint})


async def get_cameras_on_alert(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await cameras.get_list_camera_info(
                have_object=True,
                exclude_field=["regions", "showing", "tracking", "have_object"]
            )
            resp = json.loads(json.dumps({"data": data}))
            await asyncio.sleep(0.01)
            await ws.send_json(resp)
    except Exception as e:
        logger.error(f"Err at get_cameras_on_alert: {e}")
    finally:
        await ws.close()


async def test_get_cameras_on_alert(request: Request):
    server_url = AppCfg["server_address"]
    server_url = server_url.replace("http://", "ws://")
    ws_endpoint = f"{server_url}/ws/cameras-on-alert"
    return AppTemplates.TemplateResponse(
        "showText.html",
        {"request": request, "ws_endpoint": ws_endpoint})


async def get_objects_in_area_sort(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await objects.get_objects_group_by_cam_id()
            resp = json.loads(json.dumps({"data": data}))
            logger.debug(f"get_objects_in_area_sort: {resp}")
            await asyncio.sleep(0.01)
            await ws.send_json(resp)
    except Exception as e:
        logger.error(f"Err at get_objects: {e}")
    finally:
        await ws.close()


async def test_get_obj_sort_socket(request: Request):
    server_url = AppCfg["server_address"]
    server_url = server_url.replace("http://", "ws://")
    ws_endpoint = f"{server_url}/ws/objects-in-area-sort"
    return AppTemplates.TemplateResponse(
        "showText.html",
        {"request": request, "ws_endpoint": ws_endpoint})