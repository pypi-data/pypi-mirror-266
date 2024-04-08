"""Image reader module"""
import numpy as np

from ..logger import logger
from .libs_builder import build_image_reader_fn

# TODO: support for grayscale or RGBA perhaps?

# pylint: disable=broad-exception-raised
def image_read(path: str, img_lib: str = None, count: int = 5) -> np.ndarray:
    """Read an image from a path given a library"""
    f_read = build_image_reader_fn(img_lib)

    i = 0
    while True:
        try:
            return f_read(f"{path}")
        except Exception as e:
            logger.debug(f"Path: '{path}'. Exception: {e}")
            i += 1

            if i == count:
                raise Exception(e)
