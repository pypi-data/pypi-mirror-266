"""Video writer module"""
from typing import Union, List
import numpy as np
from .mpl_video import MPLVideo
from .backends import MemoryBackend
from ..logger import logger

def _make_video(video: Union[np.ndarray, List], fps: int) -> MPLVideo:
    logger.debug("Raw data provided, converting it first to MPLVideo")
    video = MPLVideo(MemoryBackend(video), fps=fps)
    return video

def video_write(video: Union[MPLVideo, np.ndarray, List], path: str, video_lib: str = None, **kwargs):
    """Write a video to the disk given a video writing library. Support for raw lists/numpy arrays of frames."""
    path = str(path) if not isinstance(path, str) else path
    if not isinstance(video, MPLVideo):
        assert "fps" in kwargs, "fps must be provided to 'video_write' when using raw arrays/lists"
        video = _make_video(video, fps=kwargs.pop("fps"))
    video.write(path, video_lib, **kwargs)
