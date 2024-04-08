"""MPLVideo module"""
from __future__ import annotations
from typing import Tuple, Callable, overload
from copy import copy, deepcopy
from pathlib import Path
import numpy as np

from .backends import MPLVideoBackend, MemoryBackend
from .utils import build_video_write_fn, build_video_read_fn, FixSizeOrderedDict
from ..image import image_resize
from ..logger import logger

MPLFrame = np.ndarray


class MPLVideo:
    """
    MPLVideo class\n
    Parameters:
        - data np.array, list or tuple of frames
        - fps frames per scond
        - shape The logical shape of the video. It can differ from the data shape, but for each access, we lazily
            resize the frames accordingly
    """

    def __init__(self, data: MPLVideoBackend, fps: int = None):
        if not isinstance(data, MPLVideoBackend):
            logger.debug(f"Data is not MPLVideoBackedn, but: {type(data)}. Making it MemoryBackend")
            data = MemoryBackend(data)
        assert len(data) > 0, "No data was provided"
        self._fps = fps if fps is not None else data.fps
        self.raw_data = data
        self._raw_len = len(data)
        self._raw_first_frame_shape = data[0].shape[0:2]
        self._frame_shape = self._raw_first_frame_shape

        self._apply_vid: MPLVideo = None
        self._apply_fn: Callable = None
        self._apply_depth = 0
        self._cached_frames = FixSizeOrderedDict({}, max_len=100)

    @property
    def path(self):
        """Return the path of the video as given by the backend"""
        return self.raw_data.path

    @property
    def fps(self):
        """The frames per second of this video"""
        return self._fps

    @fps.setter
    def fps(self, fps: float):
        self._fps = fps

    @property
    def shape(self) -> Tuple[int, int, int, int]:
        """Returns the N x H w W x 3 shapes"""
        return (len(self), *self.frame_shape, 3)

    @property
    def frame_shape(self):
        """The frame shape [H x W] of this video"""
        return self._frame_shape

    def write(self, path: str, video_lib: str = None, **kwargs):
        """
        Saves the current video to the desired path.
        Parameters
            path where to save this current file
            video_lib What video library to use to write the video
        """
        f_write = build_video_write_fn(video_lib)
        f_write(self, path, **kwargs)

    def save(self, *args, **kwargs):
        """Same as self.write()"""
        self.write(*args, **kwargs)

    @classmethod
    def read(cls, path: str, fps: int = None, vid_lib: str = None, **kwargs) -> MPLVideo:
        """
        Reads a video from a path using a video library backaned via the procedural api.
        Parameters:
        - path: The path to the video
        - fps: The frames per second
        - frame_shape: The frame shape. This is infered if not provided from the first frame or metadatas, if possible.
        - vid_lib: The video library backend.
        Returns a MPLVideo instance.
        """
        path = Path(path).resolve()
        f_read = build_video_read_fn(vid_lib)

        data = f_read(path, **kwargs)
        if fps is None:
            assert hasattr(data, "fps"), f"FPS not provided and video library {vid_lib} has no fps attribute"
            fps = data.fps
        video = cls(data, fps=fps)
        logger.debug(f"Read video (lib {'default' if vid_lib is None else vid_lib}): {repr(video)}. Path: '{path}'")
        return video


    @overload
    def __getitem__(self, key: slice) -> MPLVideo:
        ...

    @overload
    def __getitem__(self, key: int) -> np.ndarray:
        ...

    # pylint: disable=unsubscriptable-object, not-callable
    def __getitem__(self, key: int | slice):
        if isinstance(key, slice):
            res = type(self)(self.raw_data[key], self.fps)
            res._apply_fn = self._apply_fn
            res._apply_vid = self._apply_vid
            res.raw_data.path = self.path
            return res

        # Caches frame realizations for the video
        if key in self._cached_frames:
            return self._cached_frames[key]

        # Get the raw data at key frame if no apply_fns are defined
        if self._apply_vid is None:
            return self.raw_data[key]

        # the application of this video is the apply_fn on top of the previous video.
        item = self._apply_vid[key]
        result = self._apply_fn(item, self._apply_vid, key)
        self._cached_frames[key] = result

        return result

    def __setitem__(self, key, value):
        assert False, "Cannot set values to a video object. Use video.data or video[i] to get the frame."

    def __len__(self):
        return self._raw_len

    def __eq__(self, other: MPLVideo) -> bool:
        """
        Relatively expensive check to see if two videos are equal. First, we look at shape/fps. However,
        these may be equal, but the data may be different. So we look frame by frame in the end to validate.
        """
        check_n_frames = len(self) == len(other)
        check_shape = self.shape == other.shape
        check_fps = self.fps == other.fps
        if not (check_n_frames and check_shape and check_fps):
            return False

        # Next, we'll go frame by frame
        for i in range(len(self)):
            if not np.allclose(self[i], other[i]):
                return False
        return True

    def __deepcopy__(self, _):
        return type(self)(deepcopy(self.raw_data), self.fps)

    def __copy__(self):
        return type(self)(copy(self.raw_data), self.fps)

    def apply(self, apply_fn: Callable[[np.ndarray, MPLVideo, int], np.ndarray]) -> MPLVideo:
        """
        Applies a function to each frame of the self video and creates a new video with the applied function.
        The callable prototype is (item, video, t) and must return a modified frame of video[t]
        We use this because item is basically video[t], so we don't read it again.
        Return A new video where each frame is updates according to the provided callback
        """
        new_vid = type(self)(self.raw_data, self.fps)
        new_vid._apply_fn = apply_fn # pylint: disable=protected-access
        new_vid._apply_vid = self # pylint: disable=protected-access
        new_vid._apply_depth = self._apply_depth + 1 # pylint: disable=protected-access
        return new_vid

    def reshape(self, new_shape: Tuple[int, int]) -> MPLVideo:
        """reshapes the video. Note: will add a new apply_fn. Not recommended to chain reshapes."""
        assert isinstance(new_shape, (list, tuple)) and len(new_shape) == 2, new_shape
        res = self.apply(lambda item, video, t: image_resize(item, height=new_shape[0], width=new_shape[1]))
        res._frame_shape = new_shape  # pylint: disable=protected-access
        return res

    def __str__(self) -> str:
        f_str = f"[MPL Video]\n-  Frame: {self.frame_shape}.\n-  Duration: {len(self)}.\n-  FPS: {self.fps:.2f}."
        return f_str

    def __hash__(self):
        return hash(f"{id(self.raw_data)}_{self.fps}_{len(self)}")

    def __repr__(self) -> str:
        return f"MPL Video (shape:{self.shape}. fps:{self.fps:.2f}. apply_fns:{self._apply_depth})"
