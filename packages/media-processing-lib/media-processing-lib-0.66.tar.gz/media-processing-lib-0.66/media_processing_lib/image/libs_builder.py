"""Libraries builder for the image module"""
from __future__ import annotations
from typing import Callable
import os
from ..logger import logger

from .libs.pil import image_read as image_read_pil, image_write as image_write_pil, image_resize as image_resize_pil
from .libs.opencv import image_read as image_read_opencv, image_write as image_write_opencv, \
    image_resize as image_resize_opencv
from .libs.skimage import image_read as image_read_skimage, image_write as image_write_skimage, \
    image_resize as image_resize_skimage

# pylint: disable=import-outside-toplevel, unused-import
def get_available_image_libs() -> set[str]:
    """Returns a set with all the available image libraries used for reading/writing"""
    res = set()
    try:
        import PIL # noqa
        res.add("PIL")
    except ModuleNotFoundError:
        pass

    try:
        import cv2 # noqa
        res.add("opencv")
    except ModuleNotFoundError:
        pass

    try:
        import skimage # noqa
        res.add("skimage")
    except ModuleNotFoundError:
        pass

    if len(res) == 0:
        logger.info("Warning! No image libraries available. Use 'pip install -r requirements.txt'")
    return res

def build_image_reader_fn(img_lib: str) -> Callable:
    """Build the image reader function"""
    img_lib = get_default_img_lib() if img_lib is None else img_lib
    assert img_lib in get_available_image_libs(), f"Image library '{img_lib}' not in {get_available_image_libs()}"
    if img_lib == "opencv":
        return image_read_opencv
    if img_lib == "PIL":
        return image_read_pil
    if img_lib == "skimage":
        return image_read_skimage
    return None

def build_image_writer_fn(img_lib: str) -> Callable:
    """build image writer function"""
    img_lib = get_default_img_lib() if img_lib is None else img_lib
    assert img_lib in get_available_image_libs(), f"Image library '{img_lib}' not in {get_available_image_libs()}"
    if img_lib == "opencv":
        return image_write_opencv
    if img_lib == "PIL":
        return image_write_pil
    if img_lib == "skimage":
        return image_write_skimage
    return None

def build_resize_fn(resize_lib: str) -> Callable:
    """Builds the resize fn"""
    resize_lib = get_default_img_lib() if resize_lib is None else resize_lib
    assert resize_lib in get_available_image_libs(), f"Image library '{resize_lib}' not in {get_available_image_libs()}"
    if resize_lib == "skimage":
        return image_resize_skimage
    if resize_lib == "PIL":
        return image_resize_pil
    if resize_lib == "opencv":
        return image_resize_opencv
    return None

def get_default_img_lib() -> str:
    """gets the default img lib from the env variable or set opencv if it is not set"""
    backend = os.getenv("MPL_IMAGE_BACKEND")
    if not backend:
        backend = "PIL"
        logger.debug(f"MPL_IMAGE_BACKEND not set. Defaulting to '{backend}' backend")
    return backend
