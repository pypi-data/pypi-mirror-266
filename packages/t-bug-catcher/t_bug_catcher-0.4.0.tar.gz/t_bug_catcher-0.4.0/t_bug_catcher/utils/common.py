import traceback
from types import TracebackType
from typing import List


def get_frames(exc_traceback: TracebackType) -> List:
    """Get the frames of the exception.

    Args:
        exc_traceback (TracebackType): The traceback of the exception.

    Returns:
        List: The frames of the exception.
    """
    return [
        frame for frame in traceback.extract_tb(exc_traceback) if "site-packages" not in str(frame.filename).lower()
    ]
