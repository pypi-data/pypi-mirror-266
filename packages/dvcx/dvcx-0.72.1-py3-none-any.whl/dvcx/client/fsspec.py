import asyncio
import functools
import json
import logging
import multiprocessing
import os
import posixpath
from abc import ABC, abstractmethod
from collections.abc import Iterator
from datetime import datetime
from shutil import copy2
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    ClassVar,
    NamedTuple,
    Optional,
)

from botocore.exceptions import ClientError
from dvc_objects.fs.system import reflink
from fsspec.asyn import get_loop, sync
from tqdm import tqdm

from dvcx.cache import DVCXCache, UniqueId
from dvcx.client.fileslice import FileSlice
from dvcx.error import ClientError as DVCXClientError
from dvcx.node import Entry
from dvcx.nodes_fetcher import NodesFetcher
from dvcx.nodes_thread_pool import NodeChunk
from dvcx.storage import StorageURI
from dvcx.utils import TIME_ZERO

if TYPE_CHECKING:
    from fsspec.spec import AbstractFileSystem

    from dvcx.data_storage import AbstractMetastore

logger = logging.getLogger("dvcx")

FETCH_WORKERS = 100
DELIMITER = "/"  # Path delimiter.


class Bucket(NamedTuple):
    name: str
    uri: StorageURI
    created: Optional[datetime]


class Client(ABC):
    MAX_THREADS = multiprocessing.cpu_count()
    FS_CLASS: ClassVar[type["AbstractFileSystem"]]
    PREFIX: ClassVar[str]
    protocol: ClassVar[str]

    def __init__(self, name: str, fs: "AbstractFileSystem", cache: DVCXCache) -> None:
        self.name = name
        self.fs = fs
        self.cache = cache

    @staticmethod
    def get_implementation(url: str) -> type["Client"]:
        from .azure import AzureClient
        from .gcs import GCSClient
        from .local import FileClient
        from .s3 import ClientS3

        if url.lower().startswith(ClientS3.PREFIX):
            return ClientS3
        elif url.lower().startswith(GCSClient.PREFIX):
            return GCSClient
        elif url.lower().startswith(AzureClient.PREFIX):
            return AzureClient
        elif url.lower().startswith(FileClient.PREFIX) or url == "":
            return FileClient
        raise RuntimeError(f"Unsupported data source format '{url}'")

    @staticmethod
    def parse_url(
        source: str,
        metastore: "AbstractMetastore",
        cache: DVCXCache,
        **kwargs,
    ) -> tuple["Client", str]:
        cls = Client.get_implementation(source)
        storage_url, rel_path = cls.split_url(source, metastore)
        client = cls.from_name(storage_url, metastore, cache, kwargs)
        return client, rel_path

    @classmethod
    def create_fs(cls, **kwargs) -> "AbstractFileSystem":
        kwargs.setdefault("version_aware", True)
        fs = cls.FS_CLASS(**kwargs)
        fs.invalidate_cache()
        return fs

    @classmethod
    def from_name(
        cls,
        name: str,
        metastore: "AbstractMetastore",
        cache: DVCXCache,
        kwargs: dict[str, Any],
    ) -> "Client":
        return cls(name, cls.create_fs(**kwargs), cache)

    @classmethod
    def from_source(
        cls,
        uri: StorageURI,
        cache: DVCXCache,
        **kwargs,
    ) -> "Client":
        fs = cls.create_fs(**kwargs)
        return cls(fs._strip_protocol(uri), fs, cache)

    @classmethod
    def ls_buckets(cls, **kwargs) -> Iterator[Bucket]:
        for entry in cls.create_fs(**kwargs).ls(cls.PREFIX, detail=True):
            name = entry["name"].rstrip("/")
            yield Bucket(
                name=name,
                uri=StorageURI(f"{cls.PREFIX}{name}"),
                created=entry.get("CreationDate"),
            )

    @classmethod
    def is_root_url(cls, url) -> bool:
        return url == cls.PREFIX

    @property
    def uri(self) -> StorageURI:
        return StorageURI(f"{self.PREFIX}{self.name}")

    @classmethod
    def split_url(cls, url: str, metastore: "AbstractMetastore") -> tuple[str, str]:
        fill_path = url[len(cls.PREFIX) :]
        path_split = fill_path.split("/", 1)
        bucket = path_split[0]
        path = path_split[1] if len(path_split) > 1 else ""
        return bucket, path

    def url(self, path: str, expires: int = 3600, **kwargs) -> str:
        return self.fs.sign(self.get_full_path(path), expiration=expires, **kwargs)

    async def get_current_etag(self, uid: UniqueId) -> str:
        info = await self.fs._info(self.get_full_path(uid.path))
        return self.convert_info(info, "").etag

    async def get_size(self, path: str) -> int:
        return await self.fs._size(path)

    async def get_file(self, lpath, rpath, callback):
        return await self.fs._get_file(lpath, rpath, callback=callback)

    async def scandir(self, start_prefix):
        result_queue = asyncio.Queue()
        loop = get_loop()
        main_task = loop.create_task(self._fetch(start_prefix, result_queue))
        while (entry := await result_queue.get()) is not None:
            yield entry
        await main_task

    async def _fetch(self, start_prefix="", result_queue=None):
        progress_bar = tqdm(desc=f"Listing {self.uri}", unit=" objects")
        loop = get_loop()

        queue = asyncio.Queue()
        queue.put_nowait(start_prefix)

        async def worker(queue) -> None:
            while True:
                prefix = await queue.get()
                try:
                    subdirs = await self._fetch_dir(prefix, progress_bar, result_queue)
                    for subdir in subdirs:
                        queue.put_nowait(subdir)
                except Exception as exc:
                    while not queue.empty():
                        queue.get_nowait()
                        queue.task_done()
                    raise exc

                finally:
                    queue.task_done()

        try:
            workers = []
            for _ in range(FETCH_WORKERS):
                workers.append(loop.create_task(worker(queue)))

            # Wait for all fetch tasks to complete
            await queue.join()
            # Stop the workers
            excs = []
            for worker in workers:
                if worker.done() and (exc := worker.exception()):
                    excs.append(exc)
                else:
                    worker.cancel()
            if excs:
                raise excs[0]
        except ClientError as exc:
            raise DVCXClientError(
                exc.response.get("Error", {}).get("Message") or exc,
                exc.response.get("Error", {}).get("Code"),
            ) from exc
        finally:
            # This ensures the progress bar is closed before any exceptions are raised
            progress_bar.close()
            result_queue.put_nowait(None)

    async def _fetch_dir(self, prefix, pbar, result_queue) -> set[str]:
        path = f"{self.name}/{prefix}"
        infos = await self.ls_dir(path)
        files = []
        subdirs = set()
        for info in infos:
            full_path = info["name"]
            subprefix = self.rel_path(full_path)
            if info["type"] == "directory":
                name = full_path.split(DELIMITER)[-1]
                await result_queue.put(
                    [Entry.from_dir(prefix, name, last_modified=TIME_ZERO)]
                )
                subdirs.add(subprefix)
            else:
                files.append(self.convert_info(info, prefix))
        if files:
            await result_queue.put(files)
        found_count = len(subdirs) + len(files)
        pbar.update(found_count)
        return subdirs

    async def ls_dir(self, path):
        return await self.fs._ls(path, detail=True, versions=True)

    def rel_path(self, path: str) -> str:
        return self.fs.split_path(path)[1]

    def get_full_path(self, rel_path: str) -> str:
        return f"{self.PREFIX}{self.name}/{rel_path}"

    @abstractmethod
    def convert_info(self, v: dict[str, Any], parent: str) -> Entry: ...

    def fetch_nodes(
        self,
        nodes,
        shared_progress_bar=None,
    ) -> None:
        fetcher = NodesFetcher(self, self.MAX_THREADS, self.cache)
        chunk_gen = NodeChunk(self.cache, self.uri, nodes)
        fetcher.run(chunk_gen, shared_progress_bar)

    def iter_object_chunks(self, bucket, path, version=None):
        with self.fs.open(f"{bucket}/{path}", version_id=version) as f:
            chunk = f.read()
            while chunk:
                yield chunk
                chunk = f.read()

    def instantiate_object(
        self,
        uid: UniqueId,
        dst: str,
        progress_bar: tqdm,
        force: bool = False,
    ) -> None:
        if os.path.exists(dst):
            if force:
                os.remove(dst)
            else:
                progress_bar.close()
                raise FileExistsError(f"Path {dst} already exists")
        self.do_instantiate_object(uid, dst)

    def do_instantiate_object(self, uid: "UniqueId", dst: str) -> None:
        src = self.cache.get_path(uid)
        assert src is not None

        try:
            reflink(src, dst)
        except OSError:
            # Default to copy if reflinks are not supported
            copy2(src, dst)

    def open_object(self, uid: UniqueId, use_cache: bool = True) -> BinaryIO:
        """Open a file, including files in tar archives."""
        if uid.vtype == "tar":
            return self._open_tar(uid, use_cache=True)
        if use_cache and (cache_path := self.cache.get_path(uid)):
            return open(cache_path, mode="rb")
        return self.fs.open(self.get_full_path(uid.path))

    def _open_tar(self, uid: UniqueId, use_cache: bool = True):
        assert uid.location is not None
        loc_stack = json.loads(uid.location)
        if len(loc_stack) > 1:
            raise NotImplementedError("Nested v-objects are not supported yet.")
        obj_location = loc_stack[0]
        tar_path = posixpath.split(obj_location["parent"])
        parent_etag = obj_location["etag"]
        offset = obj_location["offset"]
        size = obj_location["size"]
        parent_uid = UniqueId(
            uid.storage,
            *tar_path,
            etag=parent_etag,
            size=-1,
            vtype="",
            location=None,
        )
        f = self.open_object(parent_uid, use_cache=use_cache)
        return FileSlice(f, offset, size, posixpath.basename(uid.path))

    def open(self, path: str, mode="rb") -> Any:
        return self.fs.open(self.get_full_path(path), mode=mode)

    def download(self, uid: UniqueId, *, callback=None) -> None:
        sync(get_loop(), functools.partial(self._download, uid, callback=callback))

    async def _download(self, uid: UniqueId, *, callback=None) -> None:
        if self.cache.contains(uid):
            # Already in cache, so there's nothing to do.
            return
        await self._put_in_cache(uid, callback=callback)

    def put_in_cache(self, uid: UniqueId, *, callback=None) -> None:
        sync(get_loop(), functools.partial(self._put_in_cache, uid, callback=callback))

    async def _put_in_cache(self, uid: UniqueId, *, callback=None) -> None:
        if uid.vtype == "tar":
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None, functools.partial(self._download_from_tar, uid, callback=callback)
            )
            # self._download_from_tar(uid, callback=callback)
            return
        etag = await self.get_current_etag(uid)
        if uid.etag != etag:
            raise FileNotFoundError(
                f"Invalid etag for {uid.storage}/{uid.path}: "
                f"expected {uid.etag}, got {etag}"
            )
        await self.cache.download(uid, self, callback=callback)

    def _download_from_tar(self, uid, *, callback=None):
        with self._open_tar(uid, use_cache=False) as f:
            contents = f.read()
        self.cache.store_data(uid, contents, callback=callback)
