"""Generic utils for this module"""
from typing import Callable, List
from pathlib import Path
import numpy as np


def map_apply_fn(apply_fns: List[Callable], frame: np.ndarray, video: "MPLVideo", key: int) -> np.ndarray:
    """Applies a list of fns to the video"""
    y = frame
    for fn in apply_fns:
        y = fn(y, video, key)
    return y

def get_library_root() -> Path:
    """Gets the absolute path where the library is installed"""
    return Path(__file__).parents[1].absolute()
