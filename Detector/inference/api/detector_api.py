"""
manh.truongle  - Sep 14, 2022
truonnglm.spk@gmail.com
"""
import os
import gc
import sys
import time
import torch
import logging
import numpy as np
import collections
from PIL import Image
from typing import List, Union
from inference.utils import utils
from inference.api import base_api
from hydra.utils import instantiate
from hydra.utils import to_absolute_path
from omegaconf import DictConfig, OmegaConf


logger = logging.getLogger("inf.api.Det")

DET_OBJ = collections.namedtuple("det_obj", ["box", "conf", "cls_name", "cls_id"])


class DetectorAPi(base_api.BaseAPI):
    def __init__(self, cfg: DictConfig = None, **kwargs):
        super().__init__()
        self._cache_dir = None
        self._detector = None
        if cfg is not None:
            self.init_app(cfg, **kwargs)

    def init_app(self, cfg: DictConfig, **kwargs):
        self._detector = instantiate(cfg.detector)
        self._cache_dir = to_absolute_path(cfg.cache_dir)
        if kwargs.get("init", False):
            self.init()

    def init(self, *args, **kwargs):
        logger.info("Init API ...")
        os.makedirs(self._cache_dir, exist_ok=True)
        self._detector.init()
        self._initialized = True
        logger.info("DONE.")

    def get_cls_name(self, idx: int) -> str:
        return self._detector.get_cls_name(idx)

    def _post_process(self, res: np.ndarray, *args, **kwargs):
        dets_obj = []
        for r in res:
            det_obj = DET_OBJ(box=r[:4], conf=np.round(r[4], 3),
                              cls_id=int(r[5]), cls_name=self.get_cls_name(r[5]))
            dets_obj.append(det_obj)

        return dets_obj

    def proceed(self,
                input_data: Union[np.ndarray, Image.Image],
                **kwargs) -> [List[DET_OBJ], str]:
        super(DetectorAPi, self)._check_init(logger=logger)
        e = ""
        try:
            tic = time.time()
            res = self._detector.proceed(input_data)
            res = self._post_process(res)
            elapsed = round(time.time() - tic, 5)
            logger.info(f"{os.getpid()} - Processing time: {elapsed} - {int(1/elapsed)} fps - {len(res)}")
        except Exception as ex:
            logger.error(utils.get_err_info())
            res = []
            gc.collect()
            # torch.cuda.empty_cache()
            e = str(ex)

        return res, e


# test class
if __name__ == '__main__':
    """ python3 inference/api/artwork_generator_api.py
    """
    import cv2
    from hydra import compose, initialize

    logging.basicConfig(level=logging.DEBUG)

    initialize(config_path="../../cfg")
    _cfg = compose(config_name="config")
    _cfg = _cfg.api
    print(OmegaConf.to_yaml(_cfg))
    _api = DetectorAPi(cfg=_cfg)
    _api.init()
    im = cv2.imread(sys.argv[1])
    _res, _ = _api.proceed(im)
    for _r in _res:
        print(_r.box, _r.cls_name, _r.cls_id, _r.conf)


