"""PIL image reader"""
import numpy as np
from PIL import Image


def image_read(path: str) -> np.ndarray:
    """PIL image reader"""
    # TODO: for grayscale, this returns a RGB image too
    img_pil = Image.open(path)
    img_np = np.array(img_pil, dtype=np.uint8)
    # grayscale -> 3 gray channels repeated.
    if img_pil.mode == "L":
        return np.repeat(img_np[..., None], 3, axis=-1)
    # RGB or RGBA
    return img_np[..., 0:3]
