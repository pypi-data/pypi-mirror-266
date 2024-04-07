from tarfile import TarInfo

import pytest

from dvcx.lib.file import File
from dvcx.lib.webdataset import (
    CoreFileDuplicationError,
    CoreFileNotFoundError,
    UnknownFileExtensionError,
    WebDataset,
)
from dvcx.lib.webdataset_laion import WDSLaion


class MockTarInfo(TarInfo):
    def __init__(self, name, content=b"", size=0, offset=0):
        super().__init__(name)
        self._content = content.encode() if isinstance(content, str) else content
        self.size = size
        self.offset = offset

    def isfile(self):
        return True


class MockTar:
    def __init__(self, members: list[MockTarInfo]):
        self._members = members

    def getmembers(self):
        return self._members

    def extractfile(self, tar_info: MockTarInfo):
        class TmpReader:
            def read(self):
                return tar_info._content

        return TmpReader()


def test_webdataset_basic():
    stream = File(name="nnn.tar")
    tar = MockTar(
        [
            MockTarInfo("01.jpg"),
            MockTarInfo("01.json", b'{"uid": "5678"}'),
            MockTarInfo("64.jpg"),
            MockTarInfo("64.json", b"{}"),
        ]
    )

    groups = list(WebDataset().get_tar_groups(stream, tar, ["jpg"], WDSLaion))

    assert len(groups) == 2

    (file01, laion01), (file64, laion64) = groups

    assert file01.name == "01.jpg"
    assert file01.parent == stream.name
    assert file01.location is not None
    assert isinstance(file01.location, dict)
    assert file01.location["parent"] == stream.name

    assert file64.name == "64.jpg"
    assert file64.parent == stream.name

    assert laion01.txt is None
    assert laion01.json.uid == "5678"

    assert laion64.json.uid == ""


def test_webdataset_empty():
    stream = File(name="nnn.tar")
    tar = MockTar([])

    groups = list(WebDataset().get_tar_groups(stream, tar, ["jpg"], WDSLaion))

    assert len(groups) == 0


def test_webdataset_missing_core_files():
    stream = File(name="nnn.tar")
    tar = MockTar(
        [
            MockTarInfo("01.txt"),
            MockTarInfo("01.json", b'{"uid": "5678"}'),
            MockTarInfo("64.txt"),
            MockTarInfo("64.json", b"{}"),
        ]
    )

    with pytest.raises(CoreFileNotFoundError):
        list(WebDataset().get_tar_groups(stream, tar, ["NONSENSE"], WDSLaion))


def test_webdataset_single_file_per_group():
    stream = File(name="nnn.tar")
    tar = MockTar(
        [
            MockTarInfo("01.jpg"),
            MockTarInfo("64.jpg"),
            MockTarInfo("64.json", b"{}"),
            MockTarInfo("03.jpg"),
        ]
    )

    groups = list(WebDataset().get_tar_groups(stream, tar, ["jpg"], WDSLaion))
    assert len(groups) == 3


def test_webdataset_multiple_core_extensions():
    stream = File(name="nnn.tar")
    tar = MockTar(
        [
            MockTarInfo("01.png"),
            MockTarInfo("64.png"),
            MockTarInfo("64.json", b"{}"),
            MockTarInfo("03.jpg"),
        ]
    )

    groups = list(WebDataset().get_tar_groups(stream, tar, ["jpg", "png"], WDSLaion))
    assert len(groups) == 3


def test_webdataset_core_file_duplication():
    stream = File(name="nnn.tar")
    tar = MockTar(
        [
            MockTarInfo("01.png"),
            MockTarInfo("01.jpg"),
            MockTarInfo("64.json", b"{}"),
            MockTarInfo("03.jpg"),
        ]
    )

    with pytest.raises(CoreFileDuplicationError):
        list(WebDataset().get_tar_groups(stream, tar, ["jpg", "png"], WDSLaion))


def test_webdataset_unknown_file_type():
    stream = File(name="nnn.tar")
    tar = MockTar([MockTarInfo("01.QQQQ")])

    with pytest.raises(UnknownFileExtensionError):
        list(WebDataset().get_tar_groups(stream, tar, ["jpg", "png"], WDSLaion))
