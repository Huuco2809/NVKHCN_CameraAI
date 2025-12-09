"""
truongle - Mar 29, 2023
truonglm.spk@gmail.com
"""
import os
import sys
import cv2
import json
import time
import threading
import numpy as np
import multiprocessing
from typing import Dict
from hydra import compose, initialize
from hydra.core.utils import configure_log
from hydra.core.hydra_config import HydraConfig
from inference.wrapper.camera_wrapper import Camera
from inference.api.updateDb_api import UpdateDbApi


# Cfg app
initialize(config_path="cfg", version_base="1.2")
CFG = compose(config_name="config", return_hydra_config=True, overrides=sys.argv[1:])
HydraConfig.instance().set_config(CFG)
run_dir = HydraConfig.get().run.dir
os.makedirs(run_dir, exist_ok=True)
configure_log(CFG.hydra.job_logging, CFG.hydra.verbose)

CFG = CFG.updateDb_api

# su dung cho rtsp link 
def proceed1(cam_info: Dict):
    rtsp_link = cam_info["rtsp"]
    cam_name = cam_info["camera_name"]
    max_fps = cam_info.get("max_fps", 7)

    pid = os.getpid()
    thread_name = threading.current_thread().name
    process_name = multiprocessing.current_process().name
    task_name = f"{pid}_{process_name}_{thread_name}_{cam_name}"
    print(f"{pid} - {process_name} - {thread_name} - {cam_name}")

    cap = Camera(rtsp_link)
    Updator = UpdateDbApi()
    Updator.init(cfg=CFG)
    Updator.max_fps = max_fps

    count = 0
    while True:
        try:
            tic = time.time()
            frame = cap.get_frame()
            if frame is not None:
                Updator.proceed(rtsp_link, frame, cam_name=cam_name)
            elapse = time.time() - tic
            hop_processing_time = 1 / Updator.fps
            if elapse < hop_processing_time:
                time.sleep(hop_processing_time - elapse)
            count += 1
        except Exception as e:
            print(f"{task_name} err: {e}")

# su dung cho video local, youtube link
def proceed(cam_info):
    rtsp_link = cam_info["rtsp"]
    cam_name = cam_info["camera_name"]
    max_fps = cam_info.get("max_fps", 7)

    pid = os.getpid()
    thread_name = threading.current_thread().name
    process_name = multiprocessing.current_process().name
    task_name = f"{pid}_{process_name}_{thread_name}_{cam_name}"
    print(f"{pid} - {process_name} - {thread_name} - {cam_name}")

    rtsp_link = os.path.abspath(rtsp_link)
    cap = cv2.VideoCapture(rtsp_link)
    total_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    height, width = cap.get(cv2.CAP_PROP_FRAME_HEIGHT), cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    Updator = UpdateDbApi()
    Updator.init(cfg=CFG)
    Updator.max_fps = max_fps

    count = 0
    while True:
        try:
            tic = time.time()
            ret, frame = cap.read()
            if ret:
                count += 1
                Updator.proceed(rtsp_link, frame, cam_name=cam_name)

            if count == total_frame - 1:
                cap.release()
                cap = cv2.VideoCapture(rtsp_link)
                count = 0
            elapse = time.time() - tic
            hop_processing_time = 1 / Updator.fps
            if elapse < hop_processing_time:
                time.sleep(hop_processing_time - elapse)
        except Exception as e:
            print(f"{task_name} err: {e}")


def multithreading_logic(list_cam_info):
    tasks = []
    for cam_info in list_cam_info:
        tasks.append(threading.Thread(target=proceed, args=(cam_info,)))
        tasks[-1].start()

    for task in tasks:
        task.join()


def multiprocessing_executor(list_cam_info, workers):
    k, m = divmod(len(list_cam_info), workers)
    # distributed to each worker
    _split = [list_cam_info[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(workers)]

    with multiprocessing.Pool(workers) as multiprocessing_pool:
        multiprocessing_pool.map(
            multithreading_logic,
            [_s for _s in _split]
        )


def main():
    list_cam_json = CFG.list_cam
    with open(list_cam_json, "r") as f:
        data = json.load(f)
    # data = [{"rtsp": "tmp/PETS09.webm", "camera_name": "camera_test"}]
    # data = [{"rtsp": "rtsp://conh:conh1234@113.165.166.103:554/cam/realmonitor?channel=2&subtype=0"}]

    list_cam_info = []
    for i, cam_js in enumerate(data):
        # named for each camera link
        cam_js["camera_name"] = f"camera_{i:02d}"
        list_cam_info.append(cam_js)
    multiprocessing_executor(list_cam_info, workers=CFG.workers)


if __name__ == "__main__":
    main()
