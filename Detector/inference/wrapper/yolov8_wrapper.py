"""
manh.truongle  - Apr 27, 2023
truonnglm.spk@gmail.com
"""
import os
import sys
import time
import torch
import logging
import numpy as np
from PIL import Image
from ultralytics import YOLO
from typing import Union, List
from inference.wrapper import base_wrapper


logger = logging.getLogger("inf.wrp.yoloV8")


class YoloV8Wrapper(base_wrapper.AIBaseWrapper):
    def __init__(self,
                 weight_path: str,
                 device: Union[str, int] = 0,
                 classes: List[int] = None,
                 conf: float = 0.5,
                 imgsz: int = 640,
                 *args, **kwargs
                 ):
        super().__init__()
        self._weight_path = weight_path
        self._classes = classes
        self._conf = conf
        self._imgsz = imgsz
        self._device = "cpu" if not torch.cuda.is_available() else device

    def init(self):
        tic = time.time()
        # Load model
        self._load_model()
        # Run init
        if os.path.isfile("wiki/test.jpg"):
            from PIL import Image
            for _ in range(3):
                _ = self.proceed(Image.open("wiki/test.jpg"))

        logger.debug("Init model time: {:.4f}".format(time.time() - tic))

    def _load_model(self, *args, **kwargs):
        assert os.path.isfile(self._weight_path), logger.error(f"{self._weight_path} not exists")
        self._model = YOLO(self._weight_path)
        self._model.fuse()
        self._names = self._model.names

    def _pre_process(self, *args, **kwargs):
        tic = time.time()
        # Write something
        logger.debug("Pre-process time: {:.4f}".format(time.time() - tic))

    def _post_process(self, res, *args, **kwargs):
        tic = time.time()
        # Write something
        logger.debug("Post-process time: {:.4f}".format(time.time() - tic))

    def get_cls_name(self, idx: int) -> str:
        return self._names[idx]

    def proceed(self,
                input_data: Union[np.ndarray, Image.Image],
                *args, **kwargs
                ) -> np.ndarray:
        """
        :param input_data: nd array
        :return: ndarray - [N, 6] - xmin, ymin, xmax, ymax, conf, cls
        """
        super(YoloV8Wrapper, self)._check_model_init(logger)
        # tic = time.time()

        res = self._model.predict(
            input_data,
            verbose=False,
            conf=self._conf,
            imgsz=self._imgsz,
            classes=self._classes,
            device=self._device
        )
        res = res[0]
        res = res.boxes.data.cpu().numpy()
        # torch.cuda.synchronize()
        # elapsed = time.time() - tic
        # logger.debug("Processing time: {:.4f} - {:.2f} fps".format(elapsed, 1/elapsed))
        return res


# TEST CLASS
if __name__ == '__main__':
    """
    python3.8 inference/wrapper/CLIP_wrapper.py
    """
    import cv2
    from omegaconf import OmegaConf
    from inference.utils import utils
    from hydra.utils import instantiate
    from hydra import compose, initialize

    logging.basicConfig(level=logging.DEBUG)
    torch.cuda.empty_cache()

    initialize(config_path="../../cfg")
    cfg = compose(config_name="config")
    cfg = cfg.api.detector
    # cfg.device = "cpu"
    print(OmegaConf.to_yaml(cfg))
    md = instantiate(cfg)
    im = cv2.imread(sys.argv[1])
    im = cv2.resize(im, dsize=None, fx=0.5, fy=0.5)
    for _ in range(5):
        _res = md.proceed(im)
        print(_res)
        gpu_usage = utils.get_gpu_memory()
        logger.info("gpu usage: use / total / percent: {} / {} / {}".format(*gpu_usage))
    # for _r in _res:
    #     x1, y1, x2, y2 = _r[:4]
    #     cv2.rectangle(im, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 0), 2)
    # cv2.imshow("a", im)
    # cv2.waitKey()


