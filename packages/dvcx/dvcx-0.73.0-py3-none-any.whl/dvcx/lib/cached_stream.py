import os
import shutil
import tempfile
from abc import ABC
from contextlib import AbstractContextManager

from dvcx.cache import UniqueId


class AbstractCachedStream(AbstractContextManager, ABC):
    def __init__(self, stream, size, catalog, uid: UniqueId):
        self.stream = stream
        self.size = size
        self.catalog = catalog
        self.uid = uid


class ProgressiveCacheStream(AbstractCachedStream):
    BUF_SIZE = 4096

    def __init__(self, stream, size, catalog, uid: UniqueId):
        super().__init__(stream, size, catalog, uid)

        self.target_path = self.catalog.cache.path_from_checksum(self.uid.get_hash())
        self.cached_file = None

        self.temp_file = None
        self.temp_file_pos = 0

    def __enter__(self):
        if os.path.exists(self.target_path):
            self.cached_file = open(self.target_path, mode="rb")
            return self.cached_file

        tmp_dir = self.catalog.cache.tmp_dir
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        self.temp_file = tempfile.NamedTemporaryFile(
            prefix=str(self.uid.get_hash()), dir=tmp_dir, delete=False
        )
        return self

    def __exit__(self, *args):
        self.close()

    def read(self, size=-1):
        buf = self.stream.read(size)
        pos = self.stream.tell()

        if pos >= self.temp_file_pos:
            self._cache_catch_up(pos, buf)

        return buf

    def close(self):
        if self.cached_file:
            self.cached_file.close()

        if self.temp_file:
            if self.temp_file_pos < self.size:
                self._cache_catch_up(self.size)

            self.temp_file.close()
            if not os.path.exists(self.target_path):
                os.makedirs(os.path.dirname(self.target_path), exist_ok=True)
                shutil.move(self.temp_file.name, self.target_path)

            self.stream.close()

    def _cache_catch_up(self, pos_target, latest_buf=None):
        pos_to_restore = self.stream.tell()
        try:
            remainder = pos_target - self.temp_file_pos
            self.stream.seek(self.temp_file_pos)
            while remainder > 0:
                chunk_size = min(self.BUF_SIZE, remainder)
                buf = self.stream.read(chunk_size)
                self._cache_update(buf)
                remainder -= len(buf)
        finally:
            self.stream.seek(pos_to_restore)

    def _cache_update(self, buf):
        length = len(buf)
        self.temp_file.write(buf)
        self.temp_file_pos += length

    def seek(self, offset, whence=0):
        return self.stream.seek(offset, whence)

    def tell(self):
        return self.stream.tell()


class PreCachedStream(AbstractCachedStream):
    def __init__(self, stream, size, catalog, uid: UniqueId):
        super().__init__(stream, size, catalog, uid)
        self.client = self.catalog.get_client(self.uid.storage)
        self.cached_file = None

    def get_path_in_cache(self):
        return self.catalog.cache.path_from_checksum(self.uid.get_hash())

    def __enter__(self):
        self.client.download(self.uid)
        self.cached_file = open(self.get_path_in_cache(), "rb")
        return self.cached_file

    def __exit__(self, *args):
        self.cached_file.close()


class PreDownloadStream(PreCachedStream):
    def __exit__(self, *args):
        super().__exit__(*args)
        os.remove(self.get_path_in_cache())
