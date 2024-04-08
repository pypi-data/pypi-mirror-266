"""Video reader module"""
from .mpl_video import MPLVideo


def video_read(path: str, fps: int = None, video_lib: str = None, **kwargs) -> MPLVideo:
    """
    Reads a video from a path using a video library backaned via the procedural api.
    Parameters:
    - path: The path to the video
    - fps: The frames per second
    - frame_shape: The frame shape. This is infered if not provided from the first frame or metadatas, if possible.
    - video_lib: The video library backend.
    Returns a MPLVideo instance.
    """
    return MPLVideo.read(path, fps, video_lib, **kwargs)
