"""
truongle - Apr 3, 2023
truonnglm.spk@gmail.com
detector router
"""
from .. import schemas
from ..controllers import sockets
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/ws",
                   tags=["Cameras Stream"],
                   # dependencies=[Depends(HTTPBearer())],
                   responses={
                       400: {"model": schemas.ExceptionErrors},
                       422: {"model": schemas.CustomValidationErrors}
                   },
                   )

router.add_api_websocket_route(
    "/cameras-stream/{camera_id}",
    endpoint=sockets.stream_camera
)

router.add_api_route(
    "/cameras-stream/{camera_id}",
    endpoint=sockets.test_showing,
    methods=['GET'],
    include_in_schema=False,
    response_class=HTMLResponse
)

router.add_api_websocket_route(
    "/objects-in-area",
    endpoint=sockets.get_objects
)

router.add_api_route(
    "/objects-in-area",
    methods=['GET'],
    endpoint=sockets.test_get_objs_socket,
    response_class=HTMLResponse,
    include_in_schema=False,
)

router.add_api_websocket_route(
    "/cameras-on-alert",
    endpoint=sockets.get_cameras_on_alert
)

router.add_api_route(
    "/cameras-on-alert",
    methods=['GET'],
    endpoint=sockets.test_get_cameras_on_alert,
    response_class=HTMLResponse,
    include_in_schema=False,
)

router.add_api_websocket_route(
    "/objects-in-area-sort",
    endpoint=sockets.get_objects_in_area_sort
)

router.add_api_route(
    "/objects-in-area-sort",
    methods=['GET'],
    endpoint=sockets.test_get_obj_sort_socket,
    response_class=HTMLResponse,
    include_in_schema=False,
)