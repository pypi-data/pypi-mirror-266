from datetime import datetime
from pathlib import Path
from random import getrandbits
from typing import Optional

from pydantic import Field

from dvcx.cache import UniqueId
from dvcx.lib.cached_stream import PreCachedStream, PreDownloadStream
from dvcx.lib.feature import ShallowFeature
from dvcx.lib.utils import DvcxError


class FileFeature(ShallowFeature):
    _is_file = True

    def set_file(self, stream, caching_enabled: bool) -> None:
        raise NotImplementedError()

    def open(self):
        raise NotImplementedError()


class File(FileFeature):
    source: str = Field(default="")
    parent: str = Field(default="")
    name: str
    version: str = Field(default="")
    etag: str = Field(default="")
    size: int = Field(default=0)
    vtype: str = Field(default="")
    location: Optional[dict] = Field(default=None)

    _unique_id_keys = ["source", "parent", "name", "etag", "size", "vtype", "location"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._stream = None
        self._catalog = None

    def open(self):
        return self._stream

    def set_catalog(self, catalog):
        self._catalog = catalog

    def set_file(self, stream, caching_enabled: bool) -> None:
        if self._catalog is None:
            raise DvcxError(f"Cannot set file '{stream}' without catalog")

        stream_class = PreCachedStream if caching_enabled else PreDownloadStream
        self._stream = stream_class(stream, self.size, self._catalog, self.get_uid())

    def get_uid(self):
        dump = self.model_dump()
        return UniqueId(*(dump[k] for k in self._unique_id_keys))

    def get_local_path(self) -> Optional[str]:
        """Get path to a file in a local cache.
        Return None if file is not cached. Throws an exception if cache is not setup."""
        if self._catalog is None:
            raise RuntimeError(
                "cannot resolve local file path because catalog is not setup"
            )
        return self._catalog.cache.get_path(self.get_uid())

    def get_file_suffix(self):
        return Path(self.name).suffix

    def get_file_ext(self):
        return Path(self.name).suffix.strip(".")

    def get_file_stem(self):
        return Path(self.name).stem

    def get_full_name(self):
        if not self.parent:
            return self.name
        return f"{self.parent}/{self.name}"

    def get_full_path(self):
        return f"{self.source}/{self.get_full_name()}"


class FileInfo(FileFeature):
    source: str = Field(default="")
    parent: str = Field(default="")
    name: str
    size: int = Field(default=0)
    location: Optional[dict] = Field(default=None)
    vtype: str = Field(default="")
    dir_type: int = Field(default=0)
    owner_name: str = Field(default="")
    owner_id: str = Field(default="")
    is_latest: bool = Field(default=True)
    last_modified: datetime = Field(default=datetime.min)
    version: str = Field(default="")
    etag: str = Field(default="")
    checksum: str = Field(default="")
    anno: Optional[dict] = Field(default=None)
    random: int = Field(default_factory=lambda: getrandbits(63))
