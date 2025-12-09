"""
manh.truongle  - Sep 14, 2021
truonnglm.spk@gmail.com
"""
import os
import sys
import cv2
import copy
import time
import shutil
import logging
import numpy as np
import dataclasses
from datetime import datetime, timedelta 
from typing import List, Union, Dict
from inference.api import base_api
from hydra.utils import instantiate
from hydra.utils import to_absolute_path
from omegaconf import DictConfig, OmegaConf
from inference.utils import utils, models, mask, visualize

 

logger = logging.getLogger("inf.api.updateDb")


@dataclasses.dataclass
class FrameInfo:
    create_date: datetime
    boxes: List[List[int]] = dataclasses.field(default_factory=list)
    confs: List[float] = dataclasses.field(default_factory=list)
    cls_names: List[str] = dataclasses.field(default_factory=list)
    cls_ids: List[int] = dataclasses.field(default_factory=list)
    obj_ids: List[int] = dataclasses.field(default_factory=list)
    have_object: bool = False
    in_area: List[bool] = dataclasses.field(default_factory=list)
    go_in: List[bool] = dataclasses.field(default_factory=list)
    go_out: List[bool] = dataclasses.field(default_factory=list)


class UpdateDbApi(base_api.BaseAPI):
    def __init__(self, cfg: DictConfig = None, **kwargs):
        super().__init__()
        self._cache_dir = None
        self._data_dir = None
        self._media_dir = None
        self._video_dir = None

        self._detector = None
        self._db = None
        self._sort = None
        self._sort_cfg = None
        self._count = 0
        self._fps = 2
        self._max_fps = 7
        self._previous_frame = FrameInfo(create_date=datetime.utcnow())
        if cfg is not None:
            self.init(cfg, **kwargs)

        # init video writor
        self._vid_writer = None
        self._vid_count = 0

    @property
    def max_fps(self):
        return self._max_fps

    @max_fps.setter
    def max_fps(self, value: int):
        self._max_fps = value

    @property
    def fps(self):
        return self._fps

    def _init_sort(self):
        self._sort = instantiate(self._sort_cfg)

    def _del_sort(self):
        del self._sort
        self._sort = None
        self._previous_frame = FrameInfo(create_date=datetime.utcnow())

    def _update_count(self):
        self._count += 1
        if self._count >= 50:
            self._count = 0

    def init(self, cfg: DictConfig, *args, **kwargs):
        logger.info("Init API ...")

        # directory
        self._cache_dir = to_absolute_path(cfg.cache_dir)
        os.makedirs(self._cache_dir, exist_ok=True)
        self._data_dir = to_absolute_path(cfg.data_dir)
        os.makedirs(self._data_dir, exist_ok=True)
        self._media_dir = to_absolute_path(cfg.media_dir)
        os.makedirs(self._media_dir, exist_ok=True)
        self._video_dir = to_absolute_path(cfg.video_dir)
        os.makedirs(self._video_dir, exist_ok=True)

        # modules
        # # Detector
        self._detector = instantiate(cfg.detector)
        self._detector.init()
        # # Database manage
        self._db = instantiate(cfg.database)
        # # Sort
        self._sort_cfg = cfg.sort

        self._initialized = True
        logger.info("DONE.")
    
    def _write_thumbnail(self, cam_id: str, image: np.ndarray):
        thumbnail = os.path.join(self._media_dir, "camera", f"{cam_id}_thumbnail.jpg")
        os.makedirs(os.path.dirname(thumbnail), exist_ok=True)
        cv2.imwrite(thumbnail, image)
        logger.debug(f"write thumbnail at {thumbnail}")
        return thumbnail

    def _init_cameras_info(self, rtsp: str, image: np.ndarray, cam_name: str) -> Dict:
        logger.info("init cameras info...")
        cam_height, cam_width, _ = image.shape
        cam_id = utils.get_uuid()
        thumbnail = self._write_thumbnail(cam_id, image)

        # pad = 200
        # regions = [
        #     [(int(cam_width/2 - pad), int(cam_height/2 - pad)), (int(cam_width/2 + pad), int(cam_height/2 - pad)),
        #      (int(cam_width/2 + pad), int(cam_height/2 + pad)), (int(cam_width/2 - pad), int(cam_height/2 + pad))]
        # ]
        # mask_path = os.path.join(self._media_dir, "camera", f"{cam_id}_mask.jpg")
        # mask.create_mask(polygons=regions, mask_pth=mask_path, image_width=cam_width, image_height=cam_height)

        # init showing
        _c = self._db.count("cameras", {"showing": True})
        showing = _c <= 15

        doc = models.CamerasModel(
            camera_id=cam_id,
            camera_name=cam_name,
            rtsp=rtsp,
            thumbnail=thumbnail,
            cam_width=cam_width,
            cam_height=cam_height,
            showing=showing,
            # mask=mask_path,
            # regions=regions,
            # tracking=True,
        )

        # insert
        r = self._db.insert("cameras", doc.dict())

        return doc.dict()

    def _get_cam_info(self, rtsp: str, image: np.ndarray, cam_name: str) -> Dict:
        res = self._db.query("cameras", query={"rtsp": rtsp})
        if len(res) == 0:
            cam_info = self._init_cameras_info(rtsp, image, cam_name)
        else:
            cam_info = res[0]

        return cam_info

    def _detect(self, input_data: np.ndarray, cam_info: Dict) -> FrameInfo:
        curr_frame = FrameInfo(create_date=datetime.utcnow())
        # get detection
        scale = 0.5
        im_rz = cv2.resize(input_data, dsize=None, fx=scale, fy=scale)
        im_rz = cv2.imencode('.jpg', im_rz)[1].tostring()
        dets = self._detector.proceed(im_rz, timeout=2)
        for d in dets:
            box = np.asarray(d["box"]) * (1 / scale)
            curr_frame.boxes.append(box.astype(int).tolist())
            curr_frame.cls_names.append(d["cls_name"])
            curr_frame.cls_ids.append(d["cls_id"])
            curr_frame.confs.append(d["conf"])
            curr_frame.obj_ids.append(-1)

        return curr_frame

    def _track(self, curr_frame: FrameInfo) -> FrameInfo:
        if self._sort is None:
            self._init_sort()

        try:
            _dets = [d + [i] for i, d in enumerate(curr_frame.boxes)]
            if len(_dets) == 0:
                _dets = np.empty((0, 5))
            trk = self._sort.update(np.asarray(_dets), filter_mode="soft")
            if trk.shape[0] > 0:
                trk_sorted = trk[np.argsort(trk[:, 5])]
                for i, d in enumerate(curr_frame.boxes):
                    curr_frame.obj_ids[i] = int(trk_sorted[i][4])
        except:
            logger.error(utils.get_err_info())
        return curr_frame

    def _get_frame_info(self, curr_frame: FrameInfo, frame: np.ndarray,
                        data_dir: str, cam_info: Dict) -> [FrameInfo, List[models.DetObject]]:
        """get frame info after detect"""
        objs = []
        try:
            for i in range(len(curr_frame.boxes)):
                box = curr_frame.boxes[i]
                cls_name = curr_frame.cls_names[i]
                cls_id = curr_frame.cls_ids[i]
                conf = curr_frame.confs[i]
                obj_id = curr_frame.obj_ids[i]

                # check area
                in_area = False
                thumbnail = ""
                if os.path.isfile(cam_info['mask']):
                    # in_area = mask.check_area(obj_point=mask.xyxy2center(box), mask_pth=cam_info['mask'])
                    # logger.debug(f"box: {box}")
                    in_area = mask.check_area_1(box, mask_pth=cam_info['mask'])
                    # crop object when object in area
                    if in_area:
                        # write crop
                        crop = frame[box[1]:box[3], box[0]:box[2]]
                        try:
                            thumbnail = os.path.join(data_dir, f"{cam_info['camera_id']}{self._count:#x}{i:#x}.jpg")
                            cv2.imwrite(thumbnail, crop)
                        except:
                            thumbnail = ""
                            logger.warning(f"crop failed: {box}")

                # # compare with previous
                go_in = False
                go_out = False
                if len(self._previous_frame.obj_ids) > 0:
                    idx = np.where(np.asarray(self._previous_frame.obj_ids) == obj_id)[0]
                    if len(idx) > 0:  # have id in previous
                        idx = idx[0]
                        cond = f"{int(self._previous_frame.in_area[idx])}{int(in_area)}"
                        # logger.debug(f"check in/out cond: {cond}")
                        if cond == "00":
                            pass
                        elif cond == "01":
                            go_in = True
                        elif cond == "10":
                            go_out = True
                        else:
                            pass
                    else:
                        go_in = in_area
                else:
                    go_in = in_area
                # logger.debug(f"in/out: {go_in}, {go_out}")

                position = ""
                regions = cam_info["regions"]

                if regions:
                    regions = np.asarray(regions)
                    regions_center = np.mean(regions, axis =1).astype(int)[0]
                    xc,yc = mask.xyxy2center(box)
                    if(xc > regions_center[0] and yc > regions_center[1]): 
                        position = "Bottom_Right"
                    if(xc > regions_center[0] and yc < regions_center[1]): 
                        position = "Top_Right"
                    if(xc < regions_center[0] and yc > regions_center[1]): 
                        position = "Bottom_Left"
                    if(xc < regions_center[0] and yc < regions_center[1]): 
                        position = "Top_Left"

                objs.append(
                    models.DetObject(
                        box=box, cls_name=cls_name, cls_id=cls_id, conf=conf,
                        in_area=in_area, go_in=go_in, go_out=go_out,
                        obj_id=obj_id, thumbnail=thumbnail,
                        position=position
                    ))
                curr_frame.in_area.append(in_area)
                curr_frame.go_in.append(go_in)
                curr_frame.go_out.append(go_out)

        except Exception as e:
            logger.error(utils.get_err_info())

        curr_frame.have_object = any(curr_frame.in_area)
        return curr_frame, objs


    def _proceed_image(self, curr_frame: FrameInfo, frame: np.ndarray, frame_thumbnail: str,
                       cam_info: Dict, data_dir: str) -> [Dict, FrameInfo]:

        tic = time.perf_counter()
        # track
        if self._previous_frame.have_object and cam_info["tracking"]:
            curr_frame = self._track(curr_frame)
        # calculate information
        curr_frame, objs = self._get_frame_info(curr_frame, frame, data_dir, cam_info)
        self._previous_frame = copy.deepcopy(curr_frame)

        # reset sort
        if not curr_frame.have_object:
            self._del_sort()

        doc = models.FramesModel(
            objects=objs,
            camera_id=cam_info["camera_id"],
            create_date=curr_frame.create_date,
            have_object=any(curr_frame.in_area),
            thumbnail=frame_thumbnail,
            in_area=sum(curr_frame.in_area),
            go_in=sum(curr_frame.go_in),
            go_out=sum(curr_frame.go_out),
        )
        logger.debug(f"proceed image: {time.perf_counter() - tic}")

        return doc.dict(), curr_frame
    
    def _update_thumbnail(self, cam_id: str, image: np.ndarray):
        # write thumbnail
        thumbnail = self._write_thumbnail(cam_id, image)
        
        # Update cameras
        self._db.update("cameras",
                        {"camera_id": cam_id},
                        {"thumbnail": thumbnail}
                        )
    
    def _write_video(self, camera_name: str, have_object: bool, image: np.ndarray):
        fps = 10
        max_duration = 10*60*fps # 10 minutes

        # init video writer
        if self._vid_writer is None and have_object:
            cam_height, cam_width, _ = image.shape
            date = datetime.now().strftime('%Y_%m_%d')
            prefix = datetime.now().strftime('%Y_%m_%d-%H:%M:%S')
            vid_path = os.path.join(self._video_dir, date, camera_name ,f"{camera_name}-{prefix}.avi")
            os.makedirs(os.path.dirname(vid_path), exist_ok=True)

            self._vid_writer = cv2.VideoWriter(
                vid_path, 
                cv2.VideoWriter_fourcc(*'MJPG'),
                fps, (cam_width, cam_height)
                )
            self._vid_count = 0
        
        # write video
        if self._vid_writer and have_object:
            self._vid_count += 1
            self._vid_writer.write(image)
        
        # # end writer when have_object = false
        # if self._vid_writer and not have_object:
        if self._vid_count >= max_duration:
            self._vid_writer.release()
            self._vid_writer = None

    def proceed(self,
                rtsp: str,
                input_data: np.ndarray,
                cam_name: str,
                **kwargs):
        super(UpdateDbApi, self)._check_init(logger=logger)
        self._update_count()
        res = None
        e = ""
        try:
            cam_info = self._get_cam_info(rtsp, input_data, cam_name)

            # write frame thumbnail:
            data_dir = os.path.join(self._media_dir, "frames")
            os.makedirs(data_dir, exist_ok=True)
            frame_thumbnail = os.path.join(self._media_dir, f"{cam_info['camera_id']}{self._count:#x}.jpg")
            cv2.imwrite(frame_thumbnail, input_data)
            logger.debug(f"frame thumbnail: {frame_thumbnail}")

            # get detection
            curr_frame = self._detect(input_data, cam_info)
            logger.debug(f"num det: {len(curr_frame.boxes)}")

            doc, curr_frame = self._proceed_image(
                curr_frame=curr_frame, frame=input_data, frame_thumbnail=frame_thumbnail,
                cam_info=cam_info, data_dir=data_dir)

            # insert frames
            r = self._db.insert("frames", doc)

            # Update cameras
            self._db.update("cameras",
                            {"camera_id": cam_info["camera_id"]},
                            {"have_object": any(curr_frame.in_area)}
                            )
            # set fps
            self._fps = self._max_fps if curr_frame.have_object else 2
            
            # update thumbnail
            now = datetime.now()
            if now.minute % 5 == 0 and now.second == 0:
                self._update_thumbnail(
                    cam_id=cam_info["camera_id"], 
                    image=input_data
                    )
            
            # write video
            have_object = any(curr_frame.in_area)
            self._write_video(cam_info["camera_name"], have_object, input_data)

            # clear video folder
            now = datetime.utcnow()
            midnight = now.hour==0 and now.minute==0
            if midnight:
                for _dir in os.listdir(self._video_dir):
                    _tmp = datetime.strptime(_dir, '%Y_%m_%d')
                    if (now.date() - _tmp.date()) > timedelta(1): # greater 3 days
                        # remove folder
                        shutil.rmtree(os.path.join(self._video_dir, _dir))

        except Exception as ex:
            logger.error(utils.get_err_info())
            e = str(ex)

        return res, e


# test class
if __name__ == '__main__':
    """ python3.10 inference/api/artwork_generator_api.py
    """
    from hydra import compose, initialize

    logging.basicConfig(level=logging.DEBUG)

    initialize(config_path="../../cfg")
    _cfg = compose(config_name="config")
    _cfg = _cfg.updateDb_api
    print(OmegaConf.to_yaml(_cfg))
    _api = UpdateDbApi()
    _api.init(cfg=_cfg)

    im = cv2.imread("tmp/test01.jpg")
    # _api.proceed(rtsp="rtsp://test", input_data=im)
