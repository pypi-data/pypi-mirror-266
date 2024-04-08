"""ImageIO video reader"""
from typing import Tuple, List, Union
import math
from overrides import overrides
import numpy as np
import imageio.v3 as iio

from .mpl_video_backend import MPLVideoBackend, MPLFrame
from ...logger import logger

ReadReturnType = Tuple[np.ndarray, int, List[int], int]


class MPLImageIOBackend(MPLVideoBackend):
    """MPLImageIOBackend implementation"""

    def __init__(self, path: str, n_frames: int = None):
        super().__init__(path)
        self._iter_reader = iio.imiter(path, plugin="pyav")
        self.metadata = iio.immeta(path, plugin="pyav")

        self.fps = self.metadata["fps"]
        # Accumulate all frames in this buffer
        self._raw_data = []
        self._raw_n_frames = math.ceil(self.metadata["duration"] * self.metadata["fps"])
        self.n_frames = self._raw_n_frames if n_frames is None else n_frames
        assert (
            self.n_frames <= self._raw_n_frames
        ), f"Requested {self.n_frames}. Raw number of frames from metadata: {self._raw_n_frames}"

        # Read all frames if none are provided. We need a better way to do this perhaps.
        logger.debug(f"ImageIO MPLBackend. Path: {path}. N frames: {self.n_frames}. FPS: {self.fps}")

    @property
    @overrides
    def is_supported_format(self) -> bool:
        return self.path.suffix in  [".mp4", ".avi", ".gif"], f"Got {self.path.suffix}"

    @overrides
    def __getitem__(self, key: Union[int, slice]) -> Union[MPLFrame, List[MPLFrame]]:
        assert isinstance(key, int), f"Got {type(key)}"
        assert key < self.n_frames, f"Out of bounds: frame {key} >= {self.n_frames}"
        if key < len(self._raw_data):
            return self._raw_data[key]

        n_left = key - len(self._raw_data) + 1
        while n_left > 0:
            new_frame = next(self._iter_reader)[..., 0:3]
            self._raw_data.append(new_frame)
            n_left -= 1
        return self._raw_data[-1]

    @overrides
    def __len__(self) -> int:
        return self.n_frames
