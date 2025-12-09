"""
manh.truongle  - Nov 23, 2021
truonnglm.spk@gmail.com
read camera wrapper
"""

import cv2
import time
import logging
import threading

logger = logging.getLogger("inf.wrp.cam")


class Camera:
    last_frame = None
    last_ready = None
    lock = threading.Lock()

    def __init__(self, rtsp_link: str):
        self._rtsp_link = rtsp_link
        self._tic = None
        self._need_reinit = False
        self.init()
        # thread = threading.Thread(target=self.rtsp_cam_buffer, args=(capture,))
        # thread.daemon = True
        # thread.start()
        # logger.debug(f"thread name: {threading.current_thread().name}")

    def init(self):
        capture = cv2.VideoCapture(self._rtsp_link, apiPreference=cv2.CAP_FFMPEG)
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 3)
        self._thread = threading.Thread(target=self.rtsp_cam_buffer, args=(capture,))
        self._thread.daemon = True
        self._thread.start()
        logger.debug(f"thread name: {threading.current_thread().name}")

    def reinit(self):
        if self._thread.is_alive():
            # logger.warning(f"join thread {self._rtsp_link}")
            self._thread.join()
        self.init()
        self._tic = None
        self._need_reinit = False
        logger.warning(f"reinit {self._rtsp_link}")

    def rtsp_cam_buffer(self, capture: cv2.VideoCapture):
        while True:
            with self.lock:
                # capture.grab()
                # self.last_ready, self.last_frame = capture.retrieve()
                self.last_ready, self.last_frame = capture.read()
                if self._need_reinit:
                    break

    def get_frame(self):
        if (self.last_ready is not None) and (self.last_frame is not None):
            return self.last_frame.copy()
        else:
            if self._tic is None:
                self._tic = time.time()
            # logger.warning(f"{self._rtsp_link} none  - {time.time() - self._tic} s")
            if (time.time() - self._tic) > 60:
                self._need_reinit = True
                self.reinit()
            return None
