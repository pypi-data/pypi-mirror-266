"""border utils"""
from __future__ import annotations
import numpy as np
from ...logger import logger

def image_add_border(image: np.ndarray, color: tuple[int, int, int] | int, thicc: int | None,
                     add_x: bool = False, inplace: bool = False) -> np.ndarray:
    """
    Given an image, add rectangles to it on each side. Optionally, cross it with an X (1 line to each diagonal).
    The original image is not altered unless inplace is set to True.
    Parameters:
    - image The image that is bordered.
    - color The color of the border. Must be a [0:255] tuple.
    """
    assert len(image.shape) == 3, f"Wrong image shape: {image.shape}"
    assert thicc is None or (isinstance(thicc, int) and thicc > 0), thicc
    color = [color, color, color] if isinstance(color, int) else color
    assert len(color) == 3, f"Wrong color shape: {color}"
    h, w = image.shape[0: 2]
    if thicc is None:
        logger.debug2(f"Thicc not provided, defaulting to {thicc}, based on {h=} and {w=}.")
        thicc = max(1, min(7, h // 33)) if h >= w else max(1, min(7, w // 33)) # heuristic, to be changed if it's bad.

    idx = np.linspace(0, 1, max(h, w))
    x = np.arange(w) if h >= w else np.round(idx * (w - 1)).astype(int)
    y = np.arange(h) if w >= h else np.round(idx * (h - 1)).astype(int)

    new_image = image if inplace else image.copy()
    if add_x:
        for t in range(thicc):
            new_image[np.clip(y + t, 0, h - 1), np.clip(x, 0, w - 1)] = color
            new_image[np.clip(h - (y + 1 + t), 0, h - 1), np.clip(x, 0, w - 1)] = color
    new_image[0: thicc] = color
    new_image[-thicc:] = color
    new_image[:, 0: thicc] = color
    new_image[:, -thicc:] = color
    return new_image
