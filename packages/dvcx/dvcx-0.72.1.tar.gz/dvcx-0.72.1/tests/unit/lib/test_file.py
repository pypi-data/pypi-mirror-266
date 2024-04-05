import io

import pytest

from dvcx.cache import UniqueId
from dvcx.catalog import Catalog
from dvcx.catalog.loader import get_id_generator, get_metastore, get_warehouse
from dvcx.lib.file import File
from dvcx.lib.utils import DvcxError


def test_uid_missing_location():
    name = "my_name"
    vtype = "vt1"

    stream = File(name=name, vtype=vtype)
    assert stream.get_uid() == UniqueId("", "", name, "", 0, vtype, None)


def test_uid_location():
    name = "na_me"
    vtype = "some_random"
    loc = {"e": 42}

    stream = File(name=name, vtype=vtype, location=loc)
    assert stream.get_uid() == UniqueId("", "", name, "", 0, vtype, loc)


def test_file_stem():
    s = File(name=".file.jpg.txt")
    assert s.get_file_stem() == ".file.jpg"


def test_file_ext():
    s = File(name=".file.jpg.txt")
    assert s.get_file_ext() == "txt"


def test_file_suffix():
    s = File(name=".file.jpg.txt")
    assert s.get_file_suffix() == ".txt"


def test_full_name():
    name = ".file.jpg.txt"
    f = File(name=name)
    assert f.get_full_name() == name

    parent = "dir1/dir2"
    f = File(name=name, parent=parent)
    assert f.get_full_name() == f"{parent}/{name}"


# @pytest.fixture
# def cache(tmp_path):
#     return DVCXCache(str(tmp_path / "cache"), str(tmp_path / "tmp"))


@pytest.fixture
def catalog(tmp_path):
    id_generator = get_id_generator()
    return Catalog(
        id_generator,
        get_metastore(id_generator),
        get_warehouse(id_generator),
        str(tmp_path / "cache"),
        str(tmp_path / "tmp"),
    )


def test_cache_get_path(catalog: Catalog):
    stream = File(name="test.txt1", source="s3://mybkt")
    stream.set_catalog(catalog)

    uid = stream.get_uid()
    data = b"some data is heRe"
    catalog.cache.store_data(uid, data)

    path = stream.get_local_path()
    assert path is not None

    with open(path, mode="rb") as f:
        assert f.read() == data


def test_set_file_no_catalog(catalog):
    stream = File(name="name33")
    with pytest.raises(DvcxError):
        stream.set_file(io.StringIO(), False)


def test_cache_get_path_without_cache():
    stream = File(name="test.txt1", source="s3://mybkt")
    with pytest.raises(RuntimeError):
        stream.get_local_path()
