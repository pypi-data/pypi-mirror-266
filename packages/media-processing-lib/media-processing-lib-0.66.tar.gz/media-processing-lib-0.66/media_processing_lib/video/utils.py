"""Generic utility file for videos"""
from typing import Set, Callable
from collections import OrderedDict
import os
from ..logger import logger
from .backends import MPLImageIOBackend, DiskBackend, MPLDecordBackend, MPLPimsBackend, MPLOpenCVBackend
from .writer.imageio import video_write as video_write_imageio
from .writer.opencv import video_write as video_write_opencv

# pylint: disable=import-outside-toplevel, unused-import
def get_available_video_read_libs() -> Set[str]:
    """Returns a set with all the available video libraries used for reading"""
    # TODO: perhaps use importlib and make this better
    res = set()
    try:
        import decord

        res.add("decord")
    except ModuleNotFoundError:
        pass

    try:
        import pims

        res.add("pims")
    except ModuleNotFoundError:
        pass

    try:
        import cv2

        res.add("opencv")
    except ModuleNotFoundError:
        pass

    try:
        import imageio

        res.add("imageio")
    except ModuleNotFoundError:
        pass

    res.add("disk")

    if len(res) == 1:
        logger.warning("Warning! No video libraries available. Use 'pip install -r requirements.txt'")
    return res


# pylint: disable=import-outside-toplevel, unused-import
def get_available_video_write_libs() -> Set[str]:
    """Returns a set with all the available video libraries used for writing"""
    # TODO: perhaps use importlib and make this better
    res = set()
    try:
        import cv2

        res.add("opencv")
    except ModuleNotFoundError:
        pass

    try:
        import imageio

        res.add("imageio")
    except ModuleNotFoundError:
        pass

    if len(res) == 0:
        logger.info("Warning! No video libraries available. Use 'pip install -r requirements.txt'")
    return res


def build_video_read_fn(video_lib: str) -> Callable[[int], "MPLFrame"]:
    """Builds the video read function"""
    video_lib = get_default_video_read_lib() if video_lib is None else video_lib
    assert video_lib in get_available_video_read_libs(), video_lib
    if video_lib == "pims":
        return MPLPimsBackend
    if video_lib == "imageio":
        return MPLImageIOBackend
    if video_lib == "disk":
        return DiskBackend
    if video_lib == "opencv":
        return MPLOpenCVBackend
    if video_lib == "decord":
        return MPLDecordBackend
    assert False, "Unknown video lib: '{video_lib}'"


def build_video_write_fn(video_lib: str) -> Callable[["MPLVideo", str], None]:
    """Builds the video write fn"""
    video_lib = get_default_video_write_lib() if video_lib is None else video_lib
    assert (
        video_lib in get_available_video_write_libs()
    ), f"Video library '{video_lib}' not in '{get_available_video_write_libs()}'"
    if video_lib == "imageio":
        return video_write_imageio
    if video_lib == "opencv":
        return video_write_opencv
    assert False, f"Unknown video lib: '{video_lib}'"


def default_frame_apply_fn(frame, _, __) -> "MPLFrame":
    """Identity function for MPLVideoApply"""
    return frame


def get_default_video_read_lib() -> str:
    """get the default video read lib"""
    backend = os.getenv("MPL_VIDEO_READ_BACKEND")
    if not backend:
        backend = "pims"
        logger.debug(f"MPL_VIDEO_READ_BACKEND not set. Defaulting to '{backend}' backend")
    return backend


def get_default_video_write_lib() -> str:
    """get the default video write lib"""
    backend = os.getenv("MPL_VIDEO_WRITE_BACKEND")
    if not backend:
        backend = "imageio"
        logger.debug(f"MPL_VIDEO_WRITE_BACKEND not set. Defaulting to '{backend}' backend")
    return backend

class FixSizeOrderedDict(OrderedDict):
    """Fixed sized ordered dict, nicely borrowed from: https://stackoverflow.com/a/49274421/2086583"""
    def __init__(self, *args, max_len: int = 0, **kwargs):
        self._max = max_len
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        if self._max > 0:
            if len(self) > self._max:
                self.popitem(False)
