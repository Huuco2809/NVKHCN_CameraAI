"""
aioz.aiar.truongle - Apr 4, 2023
"""
import os
import logging

logging.getLogger("multipart.multipart").setLevel(logging.ERROR)

import enum
import hashlib
from . import schemas
from omegaconf import DictConfig
from .common import middlewares
from fastapi import (
    FastAPI,
    Request
)
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, ValidationError
from inference.wrapper.mongoDBAsync_wrapper import MongoDBWrapper
from inference.utils import mask as mask_utils
from inference.utils import visualize as vis_utils
from hydra.utils import to_absolute_path

logger  = logging.getLogger("app.init")

DbManage = MongoDBWrapper(init_now=False)
AppCfg = {}
AppTemplates = Jinja2Templates(directory="app/templates")


class DBCollections(enum.Enum):
    USERS = "users"
    FRAMES = "frames"
    CAMERAS = "cameras"


async def get_media_url(relpath):
    relpath = relpath.split("/media/")[-1]
    server_url = AppCfg["server_address"]
    return f"{server_url}/media/{relpath}"


async def get_cam_socket_url(camera_id):
    server_url = AppCfg["server_address"]
    server_url = server_url.replace("http://", "ws://")
    return f"{server_url}/ws/cameras-stream/{camera_id}"


def create_app(cfg: DictConfig) -> FastAPI:
    app = FastAPI(
        title="Database API",
        description="This is the API documentation",
        version="1.0.0",
        contact={
            "name": "ManhTruong-Le (Stephen)",
            "email": "truonnglm.spk@gmail.com",
        },
        license_info={
            "name": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
            "url": "http://creativecommons.org/licenses/by/4.0",
        },
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # init own lib
    AppCfg["data_dir"] = to_absolute_path(cfg.data_dir)
    AppCfg["cache_dir"] = to_absolute_path(cfg.cache_dir)
    AppCfg["media_dir"] = to_absolute_path(cfg.media_dir)
    os.makedirs(AppCfg["data_dir"], exist_ok=True)
    os.makedirs(AppCfg["cache_dir"], exist_ok=True)
    os.makedirs(AppCfg["media_dir"], exist_ok=True)
    AppCfg["server_address"] = f"{cfg.server_public.host}:{cfg.server_public.port}"

    @app.on_event("startup")
    async def startup_task():
        await DbManage.init(**cfg.database)
        # init user acc
        await DbManage.insert(DBCollections.USERS.value,
                              document={"username": "admin",
                                        "password": hashlib.sha3_256("dongnai3@123".encode()).hexdigest()})

    @app.on_event("shutdown")
    async def shutdown_task():
        await DbManage.close()

    # custom request validation
    @app.exception_handler(RequestValidationError)
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc):
        return await middlewares.validation_exc(exc, request)

    @app.middleware("http")
    async def my_middleware(request: Request, call_next):
        try:
            white_list = ["/docs", "/redoc", "/openapi.json", "/login", "/media/", "/ws/"]
            if not any(sub in request.scope["path"] for sub in white_list) and request.method != "OPTIONS":
                await middlewares.auth(request=request)
            return await call_next(request)
        except Exception as exc:
            return await middlewares.errors_handling(exc, request, call_next)

    # Register route
    ver_prefix = "v1"

    from .routers import media
    app.include_router(media.router)

    from .routers import sockets
    app.include_router(sockets.router)

    from .routers import users
    app.include_router(users.router, prefix=f"/api/{ver_prefix}")

    from .routers import cameras
    app.include_router(cameras.router, prefix=f"/api/{ver_prefix}")

    from .routers import objects
    app.include_router(objects.router, prefix=f"/api/{ver_prefix}")

    return app
