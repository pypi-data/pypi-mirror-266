"""MPLImagesPathBackend video reader"""
from typing import Tuple, List, Optional, Callable, Union
from pathlib import Path
import concurrent.futures
from overrides import overrides
import numpy as np

from .mpl_video_backend import MPLVideoBackend, MPLFrame
from ...image import image_read
from ...logger import logger

ReadReturnType = Tuple[np.ndarray, int, List[int], int]

class DiskBackend(MPLVideoBackend):
    """DiskBackend implmenetation. Reads data from the disk using pre-caching mechanisms."""

    def __init__(self, image_paths: List[Path], load_fn: Optional[Callable] = None, cache_size: int = 50):
        assert isinstance(image_paths, list), type(image_paths)
        assert len(image_paths) > 0, len(image_paths)
        assert isinstance(image_paths[0], Path), type(image_paths[0])
        assert 0 <= cache_size < 1000, cache_size
        super().__init__(image_paths[0].parent)
        logger.debug2(f"DiskBackend using a cache size of {cache_size} and double buffering.")

        self.files = np.array([str(x) for x in image_paths])
        self.load_fns = self._build_load_fns(load_fn)
        self._buffer1 = {}

        self.cache_size = cache_size
        self._executor = concurrent.futures.ThreadPoolExecutor()
        self._buffer2 = {}
        self._future2 = None
        if cache_size > 0:
            # cache first N frames
            self._future2 = self._executor.submit(self._fetch, range(cache_size))

    @property
    @overrides
    def is_supported_format(self) -> bool:
        if not self.path.is_dir():
            logger.warning(f"Path '{self.path}' is not a directory")
            return False
        return True

    @staticmethod
    def _npz_load(x: Path):
        return np.load(x)["arr_0"]

    def _build_load_fns(self, load_fn: Optional[Callable]) -> List[Callable]:
        if isinstance(load_fn, Callable):
            return [load_fn for _ in range(len(self.files))]
        logger.debug("load_fn was not provided. Infering from suffixes. Only png, npy and npz supported")
        suffix = Path(self.files[0]).suffix
        for file in self.files:
            assert Path(file).suffix == suffix, f"First path has suffix '{suffix}'. Got also '{file}'"

        if suffix == ".png":
            return [image_read for _ in range(len(self.files))]
        if suffix == ".npy":
            return [np.load for _ in range(len(self.files))]
        if suffix == ".npz":
            return [DiskBackend._npz_load for _ in range(len(self.files))]
        raise KeyError(f"Unknown suffix: '{suffix}'")

    def _fetch(self, indexes: List[int]):
        logger.debug2(f"Fetching in background indexes: [{indexes[0]}:{indexes[-1]}]")
        return {ix: self.load_fns[ix](self.files[ix]) for ix in indexes}

    # TODO: make this smarter. Double buffering and threads/multiprocesses
    @overrides
    def __getitem__(self, key: Union[int, slice]) -> Union[MPLFrame, List[MPLFrame]]:
        assert isinstance(key, int), f"Got {type(key)}. Slices not yet there."
        assert key < len(self), f"Out of bounds: frame {key} >= {len(self)}"

        if self.cache_size == 0:
            return self.load_fns[key](self.files[key])

        # cache hit
        if key in self._buffer1:
            return self._buffer1[key]

        self._buffer2 = self._future2.result()

        # 132 % 100 = 32; 132 - 32 = 100 => [100: 200)
        cache_start = key - key % self.cache_size
        cache_end = min(cache_start + self.cache_size, len(self))
        # cache hit, but in second buffer
        if key in self._buffer2:
            self._buffer1 = self._buffer2
            self._buffer2 = {}
        # cache miss, fetch next buffer now
        else:
            # read current and next line of cache
            self._buffer1 = self._fetch(range(cache_start, cache_end))
        if cache_end < len(self):
            next_cache_end = min(cache_end + self.cache_size * 2, len(self))
            self._future2 = self._executor.submit(self._fetch, range(cache_end, next_cache_end))

        return self._buffer1[key]

    @overrides
    def __len__(self) -> int:
        return len(self.files)
