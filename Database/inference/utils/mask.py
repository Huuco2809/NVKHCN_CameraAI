"""
manh.truongle  - Nov 23, 2021
truonnglm.spk@gmail.com
mask
"""
import os
import sys
import cv2
import logging
import numpy as np
import rasterio.features
from typing import List, Union, Tuple
from shapely.geometry import Polygon

POINT = Tuple[int, int]

logger = logging.getLogger("inf.util.mask")

PIX_VAL = 255


def create_mask(polygons: List[List[POINT]], mask_pth: str, image_height: int, image_width: int):
    os.makedirs(os.path.dirname(os.path.abspath(mask_pth)), exist_ok=True)
    list_poly = []
    for poly in polygons:
        poly.append(poly[0])
        list_poly.append(Polygon(poly))

    img = rasterio.features.rasterize(list_poly, out_shape=(image_height, image_width))
    cv2.imwrite(mask_pth, img.astype(np.uint8)*PIX_VAL)


def xyxy2center(box: List[int]) -> Tuple[int, int]:
    """box: x1, y1, x2, y2"""
    x1, y1, x2, y2 = box
    return int((x1 + x2) / 2), int(int((y1 + y2) / 2))


def check_area(obj_point: POINT, mask_pth: str):
    mask = cv2.imread(mask_pth, cv2.IMREAD_GRAYSCALE)
    pix = mask[obj_point[1], obj_point[0]]
    if pix == PIX_VAL:
        return True
    else:
        return False

def check_area_1(box, mask_pth: str):
    mask = cv2.imread(mask_pth, cv2.IMREAD_GRAYSCALE)
    x1, y1, x2, y2 = box
    pix1 = mask[y1, x1] == PIX_VAL
    pix2 = mask[y1, x2] == PIX_VAL
    pix3 = mask[y2, x1] == PIX_VAL
    pix4 = mask[y2, x2] == PIX_VAL
    return pix1 or pix2 or pix3 or pix4
  

if __name__ == '__main__':
    _polys = [
        [(0, 500), (100, 100), (300, 0), (450, 450), (0, 500)],
        [(550, 50), (900, 90), (950, 530), (570, 450), (550, 50)]
    ]
    im_w, im_h = 1000, 600
    m_pth = "tmp/mask_tmp.jpg"

    create_mask(_polys, m_pth, im_h, im_w)
    m = cv2.imread(m_pth, cv2.IMREAD_GRAYSCALE)
    # cv2.imshow("mask", m)

    # x, y = 200, 110
    x, y = 500, 200
    check = check_area((x, y), m_pth)
    print(f"check: {check}")
    if check:
        cv2.circle(m, (x, y), 10, (0, 0, 0), -1)
    else:
        cv2.circle(m, (x, y), 10, (255, 255, 255), -1)
    cv2.imshow("mask", m)
    cv2.waitKey()


