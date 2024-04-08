"""Utils for collage maker"""
from typing import Callable, Tuple, List
from pathlib import Path
import numpy as np

from ..image import image_read, image_add_title
from ..logger import logger

def auto_load_fn(file_path: Path) -> Callable[[Path], np.ndarray]:
    """Tries to autoload a file"""
    suffix = file_path.suffix[1:]
    if suffix in ("png", "jpg"):
        return image_read
    if suffix == "npy":
        return np.load
    if suffix == "npz":

        def f(x):
            X = np.load(x, allow_pickle=True)["arr_0"]
            try:
                _ = X.shape
            except Exception:
                X = X.item()
            return X

        return f
    assert False, f"Suffix unknown: '{suffix}'. Path: '{file_path}'"

def get_closest_square(N: int) -> Tuple[int, int]:
    """
    Given a stack of N images
    Find the closest square X>=N*N and then remove rows 1 by 1 until it still fits X

    Example: 9: 3*3; 12 -> 3*3 -> 3*4 (3 rows). 65 -> 8*8 -> 8*9. 73 -> 8*8 -> 8*9 -> 9*9
    """

    x = int(np.sqrt(N))
    r, c = x, x
    # There are only 2 rows possible between x^2 and (x+1)^2 because (x+1)^2 = x^2 + 2*x + 1, thus we can add 2 columns
    #  at most. If a 3rd column is needed, then closest lower bound is (x+1)^2 and we must use that.
    if c * r < N:
        c += 1
    if c * r < N:
        r += 1
    assert (c + 1) * r > N and c * (r + 1) > N
    return r, c

def _pad_to_max(imgs: List[np.ndarray]) -> List[np.ndarray]:
    """pad all images to the max shape of the list"""
    max_h = max(img.shape[0] for img in imgs)
    max_w = max(img.shape[1] for img in imgs)
    assert all(img.shape[2] == imgs[0].shape[2] for img in imgs)

    if all(img.shape == imgs[0].shape for img in imgs):
        return imgs

    logger.debug(f"Padding images to fit max size: {max_h}x{max_w}")
    res = []
    for img in imgs:
        new_img = np.pad(img, ((0, max_h - img.shape[0]), (0, max_w - img.shape[1]), (0, 0)), constant_values=255)
        res.append(new_img)
    return res

def collage_fn(images: List[np.ndarray], rows_cols: Tuple[int, int] = None, pad_bottom: int = 0,
               pad_right: int = 0, titles: List[str] = None, pad_to_max: bool = False, **kwargs,) -> np.ndarray:
    """
    Make a concatenated collage based on the desired r,c format
    Parameters:
    - images A stack of images
    - rows_cols Tuple for number of rows and columns
    - pad_bottom An integer to pad the images on top, only valid in rows [2: n_rows]. TODO: what is this measured in?
    - pad_right An integer to pad images on right, only valid on columns [2: n_cols]. TODO: what is this measured in?
    - titles Titles for each image. Optional.
    - pad_to_max If True, pad all images to the max size of all images. If False, all image must be the same shape.
    - kwargs are used for image_add_title method

    Return: A numpy array of stacked images according to (rows, cols) inputs.
    """
    assert len(images) > 1, "Must give at least two images to the collage"
    if rows_cols is None:
        rows_cols = get_closest_square(len(images))
        logger.debug2(f"row_cols was not set. Setting automatically to {rows_cols} based on number of images")
    assert len(rows_cols) == 2, f"rows_cols must be a tuple with 2 numbers, got: {rows_cols}"
    if np.prod(rows_cols) > len(images):
        logger.debug2(f"rows_cols: {rows_cols} greater than n images: {len(images)}. Padding with black images!")
    assert not all(x is None for x in images), "All images are None"

    if pad_to_max:
        images = _pad_to_max(images)

    shapes = [x.shape for x in [img for img in images if img is not None]]

    # np.pad uses [(0, 0), (0, 0), (0, 0)] to pad (a, b) on each channge of H,W,C. Our images may be H,W or H,W,C
    # If they are H, W, C then we care about [(0, pad_bottom), (0, pad_right), (0, 0)]
    pad = np.zeros((len(shapes[0]), 2), dtype=int)
    pad[0, 1] = pad_bottom
    pad[1, 1] = pad_right

    if any(x is None for x in images):
        logger.debug("Some images are None. Padding with black images!")
        images = [np.zeros(shapes[0], dtype=np.uint8) if x is None else x for x in images]
        shapes = [x.shape for x in images]

    if pad.sum() != 0:
        images = [np.pad(image, pad) for image in images]
        shapes = [x.shape for x in images]

    if titles is not None:
        images = [image_add_title(image, title, **kwargs) for (image, title) in zip(images, titles)]
        shapes = [x.shape for x in images]

    if np.std(shapes, axis=0).sum() != 0:
        raise ValueError(f"Shapes not equal: {shapes}. Use pad_to_max=True to pad images to max shape.")

    # Put all the results in a new array
    result = np.zeros((rows_cols[0] * rows_cols[1], *shapes[0]), dtype=np.uint8)
    result[0: len(images)] = np.array(images)
    result = result.reshape((rows_cols[0], rows_cols[1], *shapes[0]))
    result = np.concatenate(np.concatenate(result, axis=1), axis=1)
    # remove pad right from last image
    if pad_right != 0:
        result = result[:, 0: result.shape[1] - pad_right]
    if pad_bottom != 0:
        result = result[0: result.shape[0] - pad_bottom]
    return result
