"""
manh.truongle  - Nov 23, 2021
truonnglm.spk@gmail.com
call detector api
"""
import os
import sys
import time
import aiohttp
import requests
import logging
from typing import Dict, List, Union
from inference.utils import utils
from inference.wrapper import base_wrapper

logger = logging.getLogger("inf.wrp.callApi")


class detectByApiWrapper(base_wrapper.BaseWrapper):
    def __init__(self,
                 host: str,
                 port: str,
                 route: str,
                 params: Dict = None,
                 headers: Dict = None,
                 **kwargs
                 ):
        super().__init__()
        self._url = f"{host}:{port}/{route}"
        self._params = params if params else {}
        self._headers = headers if headers else {}

    @staticmethod
    def _dict2str(params: Dict):
        params_str = ""
        for k, v in params.items():
            params_str += f"{k}={v}&"
        return params_str.strip("&")

    def init(self):
        pass

    async def proceed_async(self, file_pth: str, *args, **kwargs) -> List[Dict]:
        # tic = time.perf_counter()
        assert os.path.isfile(file_pth), logger.error(f"{file_pth} not exists")
        res = []
        try:
            # url = self._url + f"?{self._dict2str(self._params)}" if len(self._params) > 0 else self._url
            form = aiohttp.FormData()
            form.add_field("file", open(file_pth, 'rb'))
            async with aiohttp.ClientSession() as session:
                async with session.post(self._url, headers=self._headers, data=form) as response:
                    if response.status == 200:
                        resp = await response.json()
                        res = resp["data"]

        except Exception as e:
            logger.error(utils.get_err_info())
            pass

        # elapsed = time.perf_counter() - tic
        # logger.debug("Processing time: {:.4f} - {:.2f} fps".format(elapsed, 1/elapsed))
        return res

    def proceed(self, input_data: Union[str, bytes], *args, **kwargs) -> List[Dict]:
        tic = time.perf_counter()
        if isinstance(input_data, str):
            assert os.path.isfile(input_data), logger.error(f"{input_data} not exists")

        res = []
        try:
            if isinstance(input_data, str):
                form = {"file": (open(input_data, 'rb'))}
            else:
                form = {"file": input_data}
            response = requests.post(self._url, headers=self._headers, files=form, timeout=kwargs.get("timeout"))
            if response.status_code == 200:
                resp = response.json()
                res = resp["data"]

        except Exception as e:
            logger.error(utils.get_err_info())
            pass

        elapsed = time.perf_counter() - tic
        logger.debug("Processing time: {:.4f} - {:.2f} fps".format(elapsed, 1/elapsed))
        return res


# TEST CLASS
if __name__ == '__main__':
    """
    python3.10 inference/wrapper/detectByApi_wrapper.py
    """
    import asyncio
    import cv2
    from omegaconf import OmegaConf
    from hydra.utils import instantiate
    from hydra import compose, initialize

    logging.basicConfig(level=logging.DEBUG)

    initialize(config_path="../../cfg")
    cfg = compose(config_name="config")
    cfg = cfg.updateDb_api.detector
    print(OmegaConf.to_yaml(cfg))
    _wrp = instantiate(cfg)
    # _res = asyncio.run(_wrp.proceed_async(file_pth=sys.argv[1]))
    fp = cv2.imread(sys.argv[1])
    fp = cv2.imencode('.jpg', fp)[1].tostring()
    _res = _wrp.proceed(input_data=fp, timeout=1)
    print(_res)

    # async def bench():
    #     tic = time.perf_counter()
    #     tasks = [_wrp.proceed(sys.argv[1]) for _ in range(10)]
    #     await asyncio.gather(*tasks)
    #     end_time = time.perf_counter()
    #     print(f"Time: {end_time - tic:.2f} seconds")
    #
    # asyncio.run(bench())
