import cv2
import time
import hydra
from omegaconf import DictConfig
from inference.api.detector_api import DetectorAPi

video_pth = "/home/aioz-truong/MonData/Project/EVN/Database/tmp/PETS09.webm"
txt_pth = "tmp/PETS09.txt"


@hydra.main(config_path="cfg", config_name="config", version_base="1.2")
def main(cfg: DictConfig):
    det_api = DetectorAPi(cfg=cfg.api)

    cap = cv2.VideoCapture(video_pth)
    total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    count = 0
    f_write = open(txt_pth, "w")
    while count <= (total-1):
        ret, frame = cap.read()
        if ret:
            frame = frame[:, :, ::-1]  # BGR-> RGB
            dets, _ = det_api.proceed(frame)
            if len(dets) > 0:
                for d in dets:
                    box = d.box.astype(int).tolist()
                    box = " ".join(map(str, box))
                    conf = d.conf
                    f_write.write(f"{count} {box} {conf}\n")
        count += 1

    f_write.close()
    cap.release()


if __name__ == '__main__':
    main()

