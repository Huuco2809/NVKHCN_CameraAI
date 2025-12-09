"""
aioz.aiar.truongle - Nov 19, 2020
visualize box
"""
import os
import sys
import cv2
import json
import logging
import numpy as np
from hashlib import md5
from PIL import ImageFont
from PIL import ImageDraw, Image
from typing import Union, List, Tuple, Dict


logger = logging.getLogger("inf.util.vis")

_LOC = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
_FONT_PATH = os.path.join(_LOC, "Ubuntu-B.ttf")

with open(os.path.join(_LOC, "color_pairs.json"), "r") as f:
    _COLORS = json.load(f)


def _color_image(image, font_color, background_color):
    return background_color + (font_color - background_color) * image / 255


def _get_label_image(text, font_color_tuple_bgr, background_color_tuple_bgr, font_size=15):
    font_face = ImageFont.truetype(_FONT_PATH, font_size)
    text_image = font_face.getmask(text)
    shape = list(reversed(text_image.size))
    bw_image = np.array(text_image).reshape(shape)

    image = [
        _color_image(bw_image, font_color, background_color)[None, ...]
        for font_color, background_color
        in zip(font_color_tuple_bgr, background_color_tuple_bgr)
    ]
    return np.concatenate(image).transpose((1, 2, 0))


def get_color(label: str = None, color: Union[str, int, Tuple] = None, mode: str = "BGR") -> [List, List]:
    if isinstance(color, str):
        clr = next((item for item in _COLORS if item["color_name"] == color), None)
    elif isinstance(color, int):
        clr = _COLORS[color % len(_COLORS)]
    elif isinstance(color, (Tuple, List)):
        clr = {"color_rgb": color}
    else:
        if label is not None:
            hex_digest = md5(label.encode()).hexdigest()
            color_index = int(hex_digest, 16) % len(_COLORS)
            clr = _COLORS[color_index]
        else:
            clr = _COLORS[np.random.randint(0, len(_COLORS) - 1)]
    if mode == "RGB":
        return list(tuple(clr["color_rgb"])), list(tuple(clr["text_rgb"]))
    else:
        return list(reversed(tuple(clr["color_rgb"]))), list(reversed(tuple(clr["text_rgb"])))


def _get_font_size(font_size: float, image_width: int, image_height: int):
    # Get font size
    if font_size < 0.1:
        font_size = int(font_size * min(image_height, image_width))
    elif font_size < 1.0:
        font_size = int(font_size * 70)
    else:
        font_size = int(font_size)
    return font_size


def draw_rect(
        image: np.ndarray,
        box: np.ndarray,
        label: str = None, color: Union[str, int, Tuple] = None,
        font_size: float = 0.05,
        thickness: int = 2):
    """
    image: ndarray - BGR
    boxes: array: xmin, ymin, xmax, ymax
    label: text
    color: name, int or tuple RGB
    color_wash: list color code RGB
    """
    image_height, image_width, _ = image.shape
    left, top, right, bottom = np.asarray(box).flatten().astype(int)
    color, text_color = get_color(label, color)

    cv2.rectangle(image, (left, top), (right, bottom), color, thickness)
    font_size = _get_font_size(font_size, image_width, image_height)

    if label:
        label_image = _get_label_image(label, text_color, color, font_size)
        label_height, label_width, _ = label_image.shape

        rectangle_height, rectangle_width = 1 + label_height, 1 + label_width

        rectangle_bottom = top
        rectangle_left = max(0, min(left - 1, image_width - rectangle_width))

        rectangle_top = rectangle_bottom - rectangle_height
        rectangle_right = rectangle_left + rectangle_width

        label_top = rectangle_top + 1

        if rectangle_top < 0:
            rectangle_top = top
            rectangle_bottom = rectangle_top + label_height + 1

            label_top = rectangle_top

        label_left = rectangle_left + 1
        label_bottom = label_top + label_height
        label_right = label_left + label_width

        rec_left_top = (rectangle_left, rectangle_top)
        rec_right_bottom = (rectangle_right, rectangle_bottom)

        cv2.rectangle(image, rec_left_top, rec_right_bottom, color, -1)

        image[label_top:label_bottom, label_left:label_right, :] = label_image


def pil_draw_poly(image: Image, poly: Union[List, Tuple], color: Union[str, int, Tuple] = None) -> Image:
    poly = [tuple(p) for p in poly]
    color, _ = get_color(color=color, mode="RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    draw.polygon(tuple(poly), fill=tuple(color + [127]))
    return image


def pil_draw_info(image: Image, objs_info: Dict, regions: List):
    try:
        for i, poly in enumerate(regions):
            image = pil_draw_poly(image, poly, color=i+5)

        draw = ImageDraw.Draw(image, "RGB")
        for obj in objs_info:
            if obj['in_area'] or obj["go_in"] or obj["go_out"]:
                box = obj["box"]
                idx = max(1, obj["obj_id"])
                # bebug for in/out
                color_name = "CyberYellow"
                if obj["go_in"] == True:
                    color_name = "BrightRed"
                if obj["go_out"] == True:
                    color_name = "NavyBlue"
                
                color, _ = get_color(color=color_name, mode="RGB")
                draw.rectangle(tuple(box), outline=tuple(color), width=3)

    except Exception as e:
        logger.error(e)
    return image


if __name__ == '__main__':
    print(get_color(label="person"))
    print(get_color(color=10, mode="RGB"))

    img = Image.open("data/media/camera/d60d5be45d044627a9f41ad598165243_thumbnail.jpg")
    cam_width, cam_height = img.width, img.height
    pad = 200
    _regions = [
        [(int(cam_width / 2 - pad), int(cam_height / 2 - pad)), (int(cam_width / 2 + pad), int(cam_height / 2 - pad)),
         (int(cam_width / 2 + pad), int(cam_height / 2 + pad)), (int(cam_width / 2 - pad), int(cam_height / 2 + pad))]
    ]
    _objs_info = [
        {"box": [316, 206, 354, 294], "obj_id": 1},
        {"box": [462, 166, 502, 246], "obj_id": 2},
        {"box": [548, 238, 582, 324], "obj_id": 3},
        {"box": [746, 302, 766, 408], "obj_id": 4},
    ]
    # im = pil_draw_poly(img, _regions[0], color=20)
    im = pil_draw_info(img, _objs_info, _regions)
    im.show("sh")
