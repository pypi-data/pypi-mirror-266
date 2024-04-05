import pytest
from fsspec.asyn import sync

from dvcx.asyn import get_loop
from dvcx.client import Client

from ..data import ENTRIES


@pytest.fixture
def client(cloud_server, cloud_server_credentials):
    uri = cloud_server.src_uri
    return Client.get_implementation(uri).from_source(
        uri, cache=None, **cloud_server.client_config
    )


def normalize_entries(entries):
    return {(e.parent, e.name) for e in entries}


def match_entries(result, expected):
    assert len(result) == len(expected)
    assert normalize_entries(result) == normalize_entries(expected)


async def find(client, prefix):
    results = []
    try:
        async for entries in client.scandir(prefix):
            results.extend(entries)
    except BaseException as exc:
        print(f"find: {repr(exc)}")
        raise
    return results


def scandir(client, prefix):
    return sync(get_loop(), find, client, prefix)


def test_scandir_error(client):
    with pytest.raises(FileNotFoundError):
        scandir(client, "bogus")


@pytest.mark.xfail
def test_scandir_not_dir(client):
    with pytest.raises(FileNotFoundError):
        scandir(client, "description")


def test_scandir_success(client):
    results = scandir(client, "")
    match_entries(results, ENTRIES)


def test_gcs_client_gets_credentials_from_env(monkeypatch, mocker):
    from dvcx.client.gcs import GCSClient

    monkeypatch.setenv("DVCX_GCP_CREDENTIALS", '{"token": "test-credentials-token"}')
    init = mocker.patch("dvcx.client.gcs.GCSFileSystem.__init__", return_value=None)
    mocker.patch("dvcx.client.gcs.GCSFileSystem.invalidate_cache", return_value=None)

    GCSClient.create_fs()

    init.assert_called_once_with(
        token={"token": "test-credentials-token"}, version_aware=True
    )
