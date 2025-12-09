"""
truongle - Apr 4, 2023
truonnglm.spk@gmail.com
"""
import os
import logging
logging.getLogger("multipart.multipart").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)

import time
from . import schemas
from .common import middlewares
from omegaconf import DictConfig
from hydra.utils import to_absolute_path
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, ValidationError
from inference.api.detector_api import DetectorAPi

detApi = DetectorAPi()
appCfg = schemas.AppCfg()


def create_app(cfg: DictConfig) -> FastAPI:
    app = FastAPI(
        title="Detector API",
        description="This is the API documentation",
        version="2.0.0",
        # terms_of_service="http://example.com/terms/",
        contact={
            "name": "ManhTruong-Le (Stephen)",
            "email": "truonnglm.spk@gmail.com",
        },
        license_info={
            "name": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
            "url": "http://creativecommons.org/licenses/by/4.0",
        },
    )

    # init own lib
    cacheDir = to_absolute_path(cfg.cache_dir)
    dataDir = to_absolute_path(cfg.data_dir)
    os.makedirs(cacheDir, exist_ok=True)
    os.makedirs(dataDir, exist_ok=True)
    appCfg.data_dir = dataDir
    appCfg.cache_dir = cacheDir

    detApi.init_app(cfg=cfg.api, init=True)

    # custom request validation
    @app.exception_handler(RequestValidationError)
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc):
        return await middlewares.validation_exc(exc, request)

    @app.middleware("http")
    async def my_middleware(request: Request, call_next):
        try:
            white_list = ["/docs", "/redoc", "/openapi.json"]
            if not any(sub in request.scope["path"] for sub in white_list):
                await middlewares.verify_api_key(request=request, api_key_path=to_absolute_path("api.key"))
            return await call_next(request)
        except Exception as exc:
            return await middlewares.errors_handling(exc, request, call_next)

    # Register route
    ver_prefix = "v1"
    from .routers import detector
    app.include_router(detector.router, prefix=f"/api/{ver_prefix}")

    return app
