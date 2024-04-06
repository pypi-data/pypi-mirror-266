import inspect
import json
import os
import re
import sys
from datetime import datetime
from json import JSONEncoder
from pathlib import Path
from types import FunctionType, ModuleType
from typing import Optional

import whispers

from .utils import logger


class _Encoder(JSONEncoder):
    """Encoder class for encoding the Episode object to json."""

    def default(self, o):
        """This method is used to encode the Episode object to json.

        Args:
            o (object): The object to be encoded.

        Returns:
            str: The json string.
        """
        if hasattr(o, "__dict__"):
            return o.__dict__
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, Path):
            return str(o)
        return JSONEncoder.default(self, o)


class StackSaver:
    """A class to save the stack trace."""

    def __init__(self):
        """Initializes the StackSaver class."""
        pass

    @staticmethod
    def strip_path(path: str):
        """A static method to strip the current working directory path from the input.

        Args:
            path (str): The path from which to strip the current working directory path.

        Returns:
            str: The stripped path.
        """
        return path.replace(os.getcwd(), "").strip(os.sep)

    @staticmethod
    def serialize_frame_info(frame_info: dict) -> dict:
        """A static method to serialize the frame info.

        Args:
            frame_info (dict): The frame info to be serialized.

        Returns:
            dict: The serialized frame info.
        """
        run_locals = {}
        run_args = {}
        if frame_info["locals"]:
            for key, value in frame_info["locals"].items():
                if isinstance(value, dict):
                    run_locals[str(key)] = value
                else:
                    run_locals[str(key)] = str(value)
        for key, value in frame_info["args"].items():
            if isinstance(value, dict):
                run_args[str(key)] = value
            else:
                run_args[str(key)] = str(value)
        serializable_frame_info = {
            "filename": frame_info["filename"],
            "function_name": frame_info["function_name"],
            "locals": run_locals,
            "args": run_args,
        }
        return serializable_frame_info

    @staticmethod
    def filter_variables(variables: dict) -> dict:
        """A static method to filter the variables.

        Args:
            variables (dict): The variables to be filtered.

        Returns:
            dict: The filtered variables.
        """
        if not isinstance(variables, dict):
            return variables
        else:
            local_variables = {}
            for var_name, var in variables.items():
                if re.match(r"^__\w+__$", var_name):
                    continue
                if isinstance(var, (ModuleType, FunctionType)):
                    continue
                local_variables[var_name] = var
            return local_variables

    def mask_credentials(self, file_path: str) -> None:
        """A method to mask the credentials in the file.

        Args:
            file_path (str): The path of the file to be masked.

        Raises:
            Exception: If the masking fails.

        Returns:
            None
        """
        with open(file_path, "r") as f:
            filedata = f.readlines()

        secrets = [secret for secret in whispers.secrets(file_path)]

        for index, line in enumerate(filedata):
            if not secrets:
                break

            for secret in secrets:
                if secret.key in line and secret.value in line:
                    filedata[index] = line.replace(secret.value, secret.value[:1] + "***")
                    secrets.pop(secrets.index(secret))
                    break

        if secrets:
            logger.warning("Failed to mask credentials")
            os.remove(file_path)
            raise Exception("Failed to mask credentials")

        with open(file_path, "w") as file:
            file.writelines(filedata)

    def save_stack_trace(self, exception: Optional[Exception] = None):
        """A method to save the stack trace.

        Args:
            exception (Exception, optional): The exception to be saved. Defaults to None.

        Returns:
            Optional[str]: The path of the saved stack trace.
        """
        try:
            frames = []
            stack_details_json = []
            tb = exception.__traceback__ if exception else sys.exc_info()[2]
            while tb is not None:
                frame = tb.tb_frame
                if "site-packages" in frame.f_code.co_filename:
                    tb = tb.tb_next
                    continue
                frames.append(frame)
                tb = tb.tb_next
            frames = frames[:3]

            for frame in frames:
                frame_info = {
                    "filename": self.strip_path(frame.f_code.co_filename),
                    "function_name": frame.f_code.co_name,
                    "locals": self.filter_variables(frame.f_locals),
                    "args": self.filter_variables(inspect.getargvalues(frame)[3]),
                }
                stack_details_json.append(self.serialize_frame_info(frame_info))

            file_path = f"stack_details_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

            with open(file_path, "w") as f:
                json.dump(stack_details_json, f, indent=4, cls=_Encoder)

            self.mask_credentials(file_path)

            return file_path
        except Exception as e:
            logger.warning(f"Failed to save stack trace: {e}")
            return
