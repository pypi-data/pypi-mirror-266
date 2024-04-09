import traceback
from datetime import date, datetime
from json import JSONEncoder
from pathlib import Path
from types import TracebackType
from typing import List


class Encoder(JSONEncoder):
    """This class is used to encode the Episode object to json."""

    def default(self, o):
        """This method is used to encode the Episode object to json.

        Args:
            o (object): The object to be encoded.

        Returns:
            str: The json string.
        """
        if hasattr(o, "__dict__"):
            return o.__dict__
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, Path):
            return str(o)
        return JSONEncoder.default(self, o)


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
