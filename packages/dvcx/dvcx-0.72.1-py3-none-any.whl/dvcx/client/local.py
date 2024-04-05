import os
import posixpath
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fsspec.implementations.local import LocalFileSystem

from dvcx.error import StorageNotFoundError
from dvcx.node import Entry

from ..storage import StorageURI
from .fsspec import Client

if TYPE_CHECKING:
    from dvcx.data_storage import AbstractMetastore


class FileClient(Client):
    FS_CLASS = LocalFileSystem
    PREFIX = "file://"
    protocol = "file"

    def __init__(
        self, name: str, fs: LocalFileSystem, cache, use_symlinks: bool = False
    ) -> None:
        super().__init__(name, fs, cache)
        self.use_symlinks = use_symlinks

    def url(self, path: str, expires: int = 3600, **kwargs) -> str:
        raise TypeError("Signed urls are not implemented for local file system")

    @classmethod
    def ls_buckets(cls, **kwargs):
        return []

    @classmethod
    def split_url(cls, url: str, metastore: "AbstractMetastore") -> tuple[str, str]:
        def _storage_exists(uri: str) -> bool:
            try:
                metastore.get_storage(StorageURI(uri))
            except StorageNotFoundError:
                return False
            return True

        # lowercasing scheme just in case it's uppercase
        scheme, rest = url.split(":", 1)
        url = f"{scheme.lower()}:{rest}"
        if _storage_exists(url):
            return LocalFileSystem._strip_protocol(url), ""
        for pos in range(len(url) - 1, len(cls.PREFIX), -1):
            if url[pos] == "/" and _storage_exists(url[:pos]):
                return LocalFileSystem._strip_protocol(url[:pos]), url[pos + 1 :]
        raise RuntimeError(f"Invalid file path '{url}'")

    @classmethod
    def from_name(
        cls, name: str, metastore: "AbstractMetastore", cache, kwargs
    ) -> "FileClient":
        use_symlinks = kwargs.pop("use_symlinks", False)
        return cls(name, cls.create_fs(**kwargs), cache, use_symlinks=use_symlinks)

    @classmethod
    def from_source(
        cls,
        uri: str,
        cache,
        use_symlinks: bool = False,
        **kwargs,
    ) -> "FileClient":
        fs = cls.create_fs(**kwargs)
        return cls(
            fs._strip_protocol(uri),
            cls.create_fs(**kwargs),
            cache,
            use_symlinks=use_symlinks,
        )

    async def get_current_etag(self, uid) -> str:
        info = self.fs.info(self.get_full_path(uid.path))
        return self.convert_info(info, "").etag

    async def get_size(self, path: str) -> int:
        return self.fs.size(path)

    async def get_file(self, lpath, rpath, callback):
        return self.fs.get_file(lpath, rpath, callback=callback)

    async def ls_dir(self, path):
        return self.fs.ls(path, detail=True)

    def rel_path(self, path):
        return posixpath.relpath(path, self.name)

    @property
    def uri(self):
        return Path(self.name).as_uri()

    def get_full_path(self, rel_path):
        full_path = Path(self.name, rel_path).as_uri()
        if rel_path.endswith("/") or not rel_path:
            full_path += "/"
        return full_path

    def convert_info(self, v: dict[str, Any], parent: str) -> Entry:
        name = posixpath.basename(v["name"])
        return Entry.from_file(
            parent=parent,
            name=name,
            etag=v["mtime"].hex(),
            is_latest=True,
            last_modified=datetime.fromtimestamp(v["mtime"], timezone.utc),
            size=v.get("size", ""),
        )

    def fetch_nodes(
        self,
        nodes,
        shared_progress_bar=None,
    ) -> None:
        if not self.use_symlinks:
            super().fetch_nodes(nodes, shared_progress_bar)

    def do_instantiate_object(self, uid, dst):
        if self.use_symlinks:
            os.symlink(Path(self.name, uid.path), dst)
        else:
            super().do_instantiate_object(uid, dst)
