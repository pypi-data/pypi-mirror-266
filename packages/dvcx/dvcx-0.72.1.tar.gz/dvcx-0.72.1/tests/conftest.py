import os
import os.path
import uuid
from collections.abc import Generator
from pathlib import PosixPath

import attrs
import pytest
import pytest_servers.exceptions
from pytest import MonkeyPatch, TempPathFactory
from upath.implementations.cloud import CloudPath

from dvcx.catalog import Catalog
from dvcx.catalog.loader import get_id_generator, get_metastore, get_warehouse
from dvcx.data_storage.sqlite import (
    SQLiteDatabaseEngine,
    SQLiteIDGenerator,
    SQLiteMetastore,
    SQLiteWarehouse,
)
from dvcx.dataset import DatasetRecord
from dvcx.utils import DVCXDir, get_env_list

from .utils import DEFAULT_TREE, get_simple_ds_query, instantiate_tree

DEFAULT_DVCX_BIN = "dvcx"
DEFAULT_DVCX_GIT_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

collect_ignore = ["setup.py"]


@pytest.fixture(scope="session")
def monkeypatch_session() -> Generator[MonkeyPatch, None, None]:
    """
    Like monkeypatch, but for session scope.
    """
    mpatch = pytest.MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session", autouse=True)
def clean_environment(
    monkeypatch_session: MonkeyPatch,
    tmp_path_factory: TempPathFactory,
) -> None:
    """
    Make sure we have a clean environment and won't write to userspace.
    """
    working_dir = str(tmp_path_factory.mktemp("default_working_dir"))
    monkeypatch_session.chdir(working_dir)
    monkeypatch_session.delenv(DVCXDir.ENV_VAR, raising=False)

    def default_root(cls: type[DVCXDir]) -> str:
        return os.path.join(working_dir, cls.DEFAULT)

    monkeypatch_session.setattr(
        "dvcx.utils.DVCXDir.default_root",
        classmethod(default_root),
    )


@pytest.fixture
def sqlite_db():
    return SQLiteDatabaseEngine.from_db_file(":memory:")


def cleanup_sqlite_db(
    db: SQLiteDatabaseEngine,
    cleanup_tables: list[str],
):
    # Wipe the DB after the test
    # Using new connection to check that the DB isn't locked
    tables = db.execute_str(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()

    # removing in reversed order because of foreign keys
    for table in reversed(cleanup_tables):
        db.execute_str(f"DROP TABLE IF EXISTS '{table}'")

    for (table,) in tables:
        name = table.replace("'", "''")
        db.execute_str(f"DROP TABLE IF EXISTS '{name}'")


@pytest.fixture
def id_generator():
    if os.environ.get("DVCX_ID_GENERATOR"):
        _id_generator = get_id_generator()
    else:
        db = SQLiteDatabaseEngine.from_db_file(":memory:")
        _id_generator = SQLiteIDGenerator(db)
    yield _id_generator
    _id_generator.cleanup_for_tests()


@pytest.fixture
def metastore(id_generator):
    if os.environ.get("DVCX_METASTORE"):
        _metastore = get_metastore(id_generator)
        yield _metastore

        _metastore.cleanup_for_tests()
    else:
        _metastore = SQLiteMetastore(id_generator, db_file=":memory:")
        yield _metastore

        cleanup_sqlite_db(_metastore.db.clone(), _metastore.default_table_names)


@pytest.fixture
def warehouse(id_generator, metastore):
    if os.environ.get("DVCX_WAREHOUSE"):
        _warehouse = get_warehouse(id_generator)
        yield _warehouse

        _warehouse.cleanup_for_tests()
    else:
        _warehouse = SQLiteWarehouse(id_generator, db_file=":memory:")
        yield _warehouse

        cleanup_sqlite_db(_warehouse.db.clone(), metastore.default_table_names)


@pytest.fixture
def catalog(id_generator, metastore, warehouse):
    return Catalog(id_generator=id_generator, metastore=metastore, warehouse=warehouse)


@pytest.fixture
def id_generator_tmpfile(tmp_path):
    if os.environ.get("DVCX_ID_GENERATOR"):
        _id_generator = get_id_generator()
    else:
        db = SQLiteDatabaseEngine.from_db_file(tmp_path / "test.db")
        _id_generator = SQLiteIDGenerator(db)
    yield _id_generator
    _id_generator.cleanup_for_tests()


@pytest.fixture
def metastore_tmpfile(tmp_path, id_generator_tmpfile):
    if os.environ.get("DVCX_METASTORE"):
        _metastore = get_metastore(id_generator_tmpfile)
        yield _metastore

        _metastore.cleanup_for_tests()
    else:
        _metastore = SQLiteMetastore(id_generator_tmpfile, db_file=tmp_path / "test.db")
        yield _metastore

        cleanup_sqlite_db(_metastore.db.clone(), _metastore.default_table_names)


@pytest.fixture
def warehouse_tmpfile(tmp_path, id_generator_tmpfile, metastore_tmpfile):
    if os.environ.get("DVCX_WAREHOUSE"):
        _warehouse = get_warehouse(id_generator_tmpfile)
        yield _warehouse

        _warehouse.cleanup_for_tests()
    else:
        _warehouse = SQLiteWarehouse(id_generator_tmpfile, db_file=tmp_path / "test.db")
        yield _warehouse

        cleanup_sqlite_db(_warehouse.db.clone(), metastore_tmpfile.default_table_names)


@pytest.fixture
def tmp_dir(tmp_path_factory, monkeypatch):
    dpath = tmp_path_factory.mktemp("dvcx-test")
    monkeypatch.chdir(dpath)
    return dpath


def pytest_addoption(parser):
    parser.addoption(
        "--dvcx-bin",
        type=str,
        default=DEFAULT_DVCX_BIN,
        help="Path to dvcx binary",
    )

    parser.addoption(
        "--dvcx-revs",
        type=str,
        help="Comma-separated list of DVCx revisions to test (overrides `--dvcx-bin`)",
    )

    parser.addoption(
        "--dvcx-git-repo",
        type=str,
        default=DEFAULT_DVCX_GIT_REPO,
        help="Path or url to dvcx git repo",
    )
    parser.addoption(
        "--azure-connection-string",
        type=str,
        help=(
            "Connection string to run tests against a real, versioned "
            "Azure storage account"
        ),
    )


class DVCXTestConfig:
    def __init__(self):
        self.dvcx_bin = DEFAULT_DVCX_BIN
        self.dvcx_revs = None
        self.dvcx_git_repo = DEFAULT_DVCX_GIT_REPO


@pytest.fixture(scope="session")
def test_config(request):
    return request.config.dvcx_config


def pytest_configure(config):
    config.dvcx_config = DVCXTestConfig()

    config.dvcx_config.dvcx_bin = config.getoption("--dvcx-bin")
    config.dvcx_config.dvcx_revs = config.getoption("--dvcx-revs")
    config.dvcx_config.dvcx_git_repo = config.getoption("--dvcx-git-repo")


@pytest.fixture(scope="session", params=[DEFAULT_TREE])
def tree(request):
    return request.param


@attrs.define
class CloudServer:
    kind: str
    src: CloudPath
    client_config: dict[str, str]

    @property
    def src_uri(self):
        if self.kind == "file":
            return self.src.as_uri()
        return str(self.src).rstrip("/")


def make_cloud_server(src_path, cloud_type, tree):
    fs = src_path.fs
    if cloud_type == "s3":
        endpoint_url = fs.client_kwargs["endpoint_url"]
        client_config = {"aws_endpoint_url": endpoint_url}
    elif cloud_type == "gcs":
        endpoint_url = fs._endpoint
        client_config = {"endpoint_url": endpoint_url}
    elif cloud_type == "azure":
        client_config = fs.storage_options.copy()
    elif cloud_type == "file":
        client_config = {}
    else:
        raise ValueError(f"invalid cloud_type: {cloud_type}")

    instantiate_tree(src_path, tree)
    return CloudServer(kind=cloud_type, src=src_path, client_config=client_config)


@attrs.define
class CloudTestCatalog:
    server: CloudServer
    working_dir: PosixPath
    catalog: Catalog

    @property
    def src(self):
        return self.server.src

    @property
    def src_uri(self):
        return self.server.src_uri

    @property
    def client_config(self):
        return self.server.client_config


@pytest.fixture(scope="session", params=["file", "s3", "gcs", "azure"])
def cloud_type(request):
    return request.param


@pytest.fixture(scope="session", params=[False, True])
def version_aware(request):
    return request.param


@pytest.fixture(scope="session")
def cloud_server(request, tmp_upath_factory, cloud_type, version_aware, tree):
    # DVCX_TEST_SKIP_MISSING_REMOTES can be set to a comma-separated list
    # of remotes to skip tests for if unavailable or "all" to skip all
    # unavailable remotes:
    #  DVCX_TEST_SKIP_MISSING_REMOTES=azure,gcs
    #  DVCX_TEST_SKIP_MISSING_REMOTES=all
    skip_missing_remotes = set(get_env_list("DVCX_TEST_SKIP_MISSING_REMOTES", []))
    try:
        if cloud_type == "azure" and version_aware:
            if conn_str := request.config.getoption("--azure-connection-string"):
                src_path = tmp_upath_factory.azure(conn_str)
            else:
                pytest.skip("Can't test versioning with Azure")
        elif cloud_type == "file":
            if version_aware:
                pytest.skip("Local storage can't be versioned")
            else:
                src_path = tmp_upath_factory.mktemp("local")
        else:
            src_path = tmp_upath_factory.mktemp(cloud_type, version_aware=version_aware)
    except pytest_servers.exceptions.RemoteUnavailable as exc:
        if "all" in skip_missing_remotes or cloud_type in skip_missing_remotes:
            pytest.skip(str(exc))
        raise

    return make_cloud_server(src_path, cloud_type, tree)


@pytest.fixture
def cloud_server_credentials(cloud_server, monkeypatch):
    if cloud_server.kind == "s3":
        cfg = cloud_server.src.fs.client_kwargs
        try:
            monkeypatch.delenv("AWS_PROFILE")
        except KeyError:
            pass
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", cfg.get("aws_access_key_id"))
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", cfg.get("aws_secret_access_key"))
        monkeypatch.setenv("AWS_SESSION_TOKEN", cfg.get("aws_session_token"))
        monkeypatch.setenv("AWS_DEFAULT_REGION", cfg.get("region_name"))


def get_cloud_test_catalog(cloud_server, tmp_path, id_generator, metastore, warehouse):
    cache_dir = tmp_path / ".dvcx" / "cache"
    cache_dir.mkdir(parents=True)
    tmpfile_dir = tmp_path / ".dvcx" / "tmp"
    tmpfile_dir.mkdir()

    catalog = Catalog(
        id_generator=id_generator,
        metastore=metastore,
        warehouse=warehouse,
        cache_dir=str(cache_dir),
        tmp_dir=str(tmpfile_dir),
        client_config=cloud_server.client_config,
    )
    result = CloudTestCatalog(
        server=cloud_server, working_dir=tmp_path, catalog=catalog
    )
    if cloud_server.kind == "file":
        catalog.add_storage(f"{result.src_uri}")
    return result


@pytest.fixture
def cloud_test_catalog(
    cloud_server,
    cloud_server_credentials,
    tmp_path,
    id_generator,
    metastore,
    warehouse,
):
    return get_cloud_test_catalog(
        cloud_server, tmp_path, id_generator, metastore, warehouse
    )


@pytest.fixture
def cloud_test_catalog_tmpfile(
    cloud_server,
    cloud_server_credentials,
    tmp_path,
    id_generator_tmpfile,
    metastore_tmpfile,
    warehouse_tmpfile,
):
    return get_cloud_test_catalog(
        cloud_server,
        tmp_path,
        id_generator_tmpfile,
        metastore_tmpfile,
        warehouse_tmpfile,
    )


@pytest.fixture
def listed_bucket(cloud_test_catalog):
    list(cloud_test_catalog.catalog.ls([cloud_test_catalog.src_uri], fields=["name"]))


@pytest.fixture
def dogs_dataset(listed_bucket, cloud_test_catalog):
    name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog
    src_uri = cloud_test_catalog.src_uri
    dataset = catalog.create_dataset_from_sources(
        name, [f"{src_uri}/dogs/*"], recursive=True
    )
    return catalog.update_dataset(
        dataset, {"description": "dogs dataset", "labels": ["dogs", "dataset"]}
    )


@pytest.fixture
def cats_dataset(listed_bucket, cloud_test_catalog):
    name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog
    src_uri = cloud_test_catalog.src_uri
    dataset = catalog.create_dataset_from_sources(
        name, [f"{src_uri}/cats/*"], recursive=True
    )
    return catalog.update_dataset(
        dataset, {"description": "cats dataset", "labels": ["cats", "dataset"]}
    )


@pytest.fixture
def simple_ds_query(cloud_test_catalog):
    return get_simple_ds_query(
        path=cloud_test_catalog.src_uri, catalog=cloud_test_catalog.catalog
    )


@pytest.fixture
def dataset_record():
    return DatasetRecord(
        id=1,
        name=f"ds_{uuid.uuid4().hex}",
        description="",
        labels=[],
        versions=[],
        shadow=False,
        status=1,
        custom_column_types={},
    )
