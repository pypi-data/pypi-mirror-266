"""MPLVideo backend -- module that defines a backend suitable for MPLVideo data reader"""
from abc import ABC, abstractmethod
from typing import Union, List, overload, Optional
from pathlib import Path
import numpy as np

MPLFrame = np.ndarray


class MPLVideoBackend(ABC):
    """MPLVideo backend implmenetation"""

    def __init__(self, path: Optional[Path]):
        self.path = Path(path) if path is not None else None
        assert self.is_supported_format, f"Path '{path}' not a supported format"

    @property
    @abstractmethod
    def is_supported_format(self) -> bool:
        """Returns if the path is a valid video according to this backend"""

    @abstractmethod
    def __len__(self) -> int:
        """Gets the length of the backend"""

    @overload
    @abstractmethod
    def __getitem__(self, key: int) -> MPLFrame:
        ...

    @overload
    @abstractmethod
    def __getitem__(self, key: slice) -> List[MPLFrame]:
        ...

    @abstractmethod
    def __getitem__(self, key: Union[int, slice]) -> Union[MPLFrame, List[MPLFrame]]:
        """Gets the item(s) at key"""
