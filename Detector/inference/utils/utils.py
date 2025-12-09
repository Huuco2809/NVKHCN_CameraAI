"""
manh.truongle - truonnglm.spk@gmail.com
utils
"""

import os
import sys
# import wave
import math
import psutil
import logging
# import whatimage
# import pillow_heif
import subprocess
import numpy as np
from PIL import Image

logger = logging.getLogger("inf.util.util")

LM_COLOR = [(255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (0, 255, 255),
            (255, 0, 255)]


# def draw_landmarks(img, landmarks):
#     """Draw bounding boxes and face landmarks on image."""
#     for ll in landmarks:
#         for j in range(5):
#             cv2.circle(img, (int(ll[j]), int(ll[j + 5])), 2, LM_COLOR[j], 2)
#
#     return img


def get_mem_and_cpu():
    process = psutil.Process(os.getpid())
    mem_total = round(int(psutil.virtual_memory().total) * 1e-6)  # Mb
    mem_usage = round(int(process.memory_full_info().rss) * 1e-6)
    mem_percent = round((mem_usage / mem_total) * 100, 2)
    cpu_total = int(psutil.cpu_count())
    cpu_usage = int(process.cpu_num())
    #     cpu_avg_percent = round(process.cpu_percent(), 2)
    return [mem_usage, mem_total, mem_percent], [cpu_usage, cpu_total]


def get_gpu_memory(idx=0):
    usage = subprocess.check_output(
        [
            'nvidia-smi', '--query-gpu=memory.used',
            '--format=csv,nounits,noheader', f'--id={idx}',
        ])
    usage = int(usage)
    total = subprocess.check_output(
        [
            'nvidia-smi', '--query-gpu=memory.total',
            '--format=csv,nounits,noheader', f'--id={idx}',
        ])
    total = int(total)
    return usage, total, round((usage / total) * 100, 2)


def get_err_info():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    text = "{}  at file {} in line {}".format(exc_obj, fname, exc_tb.tb_lineno)
    # print("err:", exc_type, exc_obj, fname, exc_tb.tb_lineno)
    return text


def find_string_between(s, first=None, last=None):
    if first is None:
        start = 0
    else:
        start = s.index(first) + len(first)
    if last is None:
        end = len(s)
    else:
        end = s.index(last, start)
    return s[start:end]


def alignment(img, left_eye, right_eye):
    # this function aligns given face in img based on left and right eye coordinates
    left_eye_x, left_eye_y = left_eye
    right_eye_x, right_eye_y = right_eye

    # find rotation direction
    if left_eye_y > right_eye_y:
        point_3rd = (right_eye_x, left_eye_y)
        direction = -1  # rotate same direction to clock
    else:
        point_3rd = (left_eye_x, right_eye_y)
        direction = 1  # rotate inverse direction of clock
    # find length of triangle edges
    a = np.linalg.norm(np.array(left_eye) - np.array(point_3rd))
    b = np.linalg.norm(np.array(right_eye) - np.array(point_3rd))
    c = np.linalg.norm(np.array(right_eye) - np.array(left_eye))
    # apply cosine rule
    if b != 0 and c != 0:  # this multiplication causes division by zero in cos_a calculation
        cos_a = (b * b + c * c - a * a) / (2 * b * c)
        angle = np.arccos(cos_a)  # angle in radian
        angle = (angle * 180) / math.pi  # radian to degree
        # -----------------------
        # rotate base image
        if direction == -1:
            angle = 90 - angle
        img = Image.fromarray(img)
        img = np.array(img.rotate(direction * angle))
    return img


def crop_align(image, boxe, landmarks, align, pad=0.1):
    """crop face and align
    image: image
    boxes: face boxe [xmin, ymin, xmax, ymax]
    align: True / False
    landmarks: landmarks: shape [5, 2], [leftEye, rightEye, Nose, leftMounth, rightMounth]
    pad: padding
    """
    xmin, ymin, xmax, ymax = boxe.astype(int)
    left_eye, right_eye = landmarks[0], landmarks[1]
    box_w, box_h = xmax - xmin, ymax - ymin
    im_h, im_w, _ = image.shape

    xmin = int(max(0, xmin - box_w * pad))
    ymin = int(max(0, ymin - box_h * pad))
    xmax = int(min(im_w, xmax + box_w * pad))
    ymax = int(min(im_h, ymax + box_h * pad))

    face_crop = image[ymin:ymax, xmin:xmax, :]
    # cv2.imshow("crop", face_crop)
    if align:
        # refine keypoint
        left_eye = left_eye - np.array([xmin, ymin])
        right_eye = right_eye - np.array([xmin, ymin])
        face_crop = alignment(face_crop, left_eye, right_eye)
        # cv2.imshow("al", face_crop)
    # cv2.waitKey()

    return face_crop


# def check_wav(wav_p, max_vol=11000):
#     # visualize(path)
#     f = wave.open(wav_p)
#     content = f.readframes(-1)
#     samples = np.frombuffer(content, dtype="int16")
#     logger.debug("Max volume {}".format(np.max(samples)))
#     return np.max(samples) > max_vol


# def fix_image_type(im):
#     """check and fix type image, convert when image type is heic, cv2 can not read
#     input: im (image_path or image bytes)
#     return: cv2 mat
#     """
#     if isinstance(im, str):  # image path
#         if os.path.isfile(im):
#             with open(im, 'rb') as f:
#                 data = f.read()
#         else:
#             return None
#     elif isinstance(im, bytes):  # read bytes
#         data = im
#     elif isinstance(im, (np.ndarray, np.generic)):  # cv MAT
#         return im
#     else:
#         return None
#     fmt = whatimage.identify_image(data)
#
#     if fmt in ['heic', 'avif']:
#         # heif_file = pyheif.read(data)
#         heif_file = pillow_heif.read(data)
#         image = Image.frombytes(
#             heif_file.mode,
#             heif_file.size,
#             heif_file.data,
#             "raw",
#             heif_file.mode,
#             heif_file.stride,
#         )
#         # image.save(dst, "JPEG")
#         image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
#     else:
#         image = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), flags=1)
#     return image


def focus_estimation(landmarks, thrs=2.0):
    """landmarks: shape [n, 5, 2], [leftEye, rightEye, Nose, leftMounth, rightMounth]"""
    focus = []
    for i in range(len(landmarks)):
        le = landmarks[i][0]
        re = landmarks[i][1]
        no = landmarks[i][2]
        lm = landmarks[i][3]
        rm = landmarks[i][4]

        l_em = (le + lm) / 2
        r_em = (re + rm) / 2
        l_dis = np.linalg.norm(l_em - no)
        r_dis = np.linalg.norm(r_em - no)
        ratio = (l_dis / r_dis) if l_dis > r_dis else (r_dis / l_dis)
        # print("ratio: ", ratio)
        if ratio > thrs:
            focus.append(0)
        else:
            focus.append(1)
    return focus


def cal_similarity(ft1, ft2, mode="L2"):
    # assert mode in ["L2", "cosine"], logger.error("Mode {} invalid, supported <L2> / <cosine>".format(mode))
    if mode not in ["L2", "cosine"]:
        mode = "L2"
        logger.warning("mode {} invalid, using <L2> mode instead".format(mode))
    # print(ft1.shape)
    if mode == "L2":
        dis = np.linalg.norm(ft1 - ft2)
    else:
        umu = np.average(ft1)
        vmu = np.average(ft2)
        u = ft1 - umu
        v = ft2 - vmu
        uv = np.average(u * v)
        uu = np.average(np.square(u))
        vv = np.average(np.square(v))
        dis = 1.0 - uv / np.sqrt(uu * vv)
    return dis


def str2bool(v):
    """
    https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise logger.error("boolean value expected")
