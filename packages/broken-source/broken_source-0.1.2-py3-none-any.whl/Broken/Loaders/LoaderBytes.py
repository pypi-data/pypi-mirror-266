from pathlib import Path
from typing import Any, Optional, Union

from attr import define

from Broken.Base import BrokenPath

from . import BrokenLoader


@define
class LoaderBytes(BrokenLoader):

    @staticmethod
    def load(value: Any=None, **kwargs) -> Optional[bytes]:
        if not value:
            return b""

        elif isinstance(value, bytes):
            return value

        elif isinstance(value, str):
            return value.encode()

        elif (path := BrokenPath(value, valid=True)):
            return path.read_bytes()

        return None

LoadableBytes = Union[bytes, str, Path, None]
