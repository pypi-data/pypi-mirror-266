"""PIL image resizer"""
import numpy as np
from PIL import Image
from ....logger import logger

def image_resize(data: np.ndarray, height: int, width: int, interpolation: str, **kwargs) -> np.ndarray:
    """PIL image resizer"""
    is_float32_image = False
    if data.dtype == np.float32 and data.min() >= 0 and data.max() <= 1:
        logger.debug("Data is float32. PIL backend suport float images out of the box. Converting to uint8 and back")
        data = (data * 255).astype(np.uint8)
        is_float32_image = True
    if data.dtype != np.uint8:
        raise TypeError(f"For PIL backend only uint8 [0:255] of float32 [0:1] images are supported. Got {data.dtype}")
    assert isinstance(height, int) and isinstance(width, int), f"Expected ints. Got h={height}. w={width}"
    img_data = Image.fromarray(data)

    # As per: https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#PIL.Image.Image.resize
    resample = {
        "nearest": Image.NEAREST,
        "bilinear": Image.BILINEAR,
        "bicubic": Image.BICUBIC,
        "lanczos": Image.LANCZOS,
    }[interpolation]

    img_resized = img_data.resize(size=(width, height), resample=resample, **kwargs)
    np_img_resized = np.array(img_resized, dtype=data.dtype)
    if is_float32_image:
        np_img_resized = np_img_resized.astype(np.float32) / 255
    return np_img_resized
