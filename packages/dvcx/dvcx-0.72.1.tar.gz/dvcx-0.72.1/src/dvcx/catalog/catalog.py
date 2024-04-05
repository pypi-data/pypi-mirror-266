import ast
import functools
import io
import json
import logging
import math
import os
import os.path
import posixpath
import subprocess
import sys
import time
import traceback
from ast import Attribute, Call, Expr, Import, Load, Name, alias
from collections.abc import Iterable, Iterator, Mapping, Sequence
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from random import shuffle
from typing import (
    TYPE_CHECKING,
    Any,
    NamedTuple,
    NoReturn,
    Optional,
    Union,
)
from uuid import uuid4

import requests
import sqlalchemy as sa
import yaml
from attrs import asdict
from fsspec.implementations.local import LocalFileSystem
from sqlalchemy import Column
from tqdm import tqdm

from dvcx.cache import DVCXCache
from dvcx.client import Client
from dvcx.config import get_remote_config, read_config
from dvcx.data_storage.schema import DATASET_CORE_COLUMN_NAMES
from dvcx.dataset import (
    DATASET_PREFIX,
    QUERY_DATASET_NAME_PREFIX,
    DatasetDependency,
    DatasetRecord,
    DatasetRow,
    DatasetStats,
    create_dataset_uri,
    parse_dataset_uri,
)
from dvcx.dataset import Status as DatasetStatus
from dvcx.error import (
    ClientError,
    DatasetInvalidVersionError,
    DatasetNotFoundError,
    DVCXError,
    InconsistentSignalType,
    PendingIndexingError,
    QueryScriptCancelError,
    QueryScriptCompileError,
    QueryScriptDatasetNotFound,
    QueryScriptRunError,
)
from dvcx.listing import Listing
from dvcx.node import DirType, Node, NodeWithPath
from dvcx.nodes_thread_pool import NodesThreadPool
from dvcx.remote.studio import StudioClient
from dvcx.sql.types import DateTime, SQLType, String
from dvcx.storage import Status, Storage, StorageStats, StorageURI
from dvcx.utils import (
    DVCXDir,
    chunk,
    dvcx_paths_join,
    import_object,
    parse_params_string,
)

from .datasource import DataSource
from .formats import IndexingFormat, apply_processors

if TYPE_CHECKING:
    from dvcx.data_storage import (
        AbstractIDGenerator,
        AbstractMetastore,
        AbstractWarehouse,
    )


logger = logging.getLogger("dvcx")

DEFAULT_DATASET_DIR = "dataset"
DATASET_FILE_SUFFIX = ".edvcx"

TTL_INT = 4 * 60 * 60
PYTHON_SCRIPT_WRAPPER_CODE = "__ds__"

INDEX_INTERNAL_ERROR_MESSAGE = "Internal error on indexing"
DATASET_INTERNAL_ERROR_MESSAGE = "Internal error on creating dataset"
# exit code we use if last statement in query script is not instance of DatasetQuery
QUERY_SCRIPT_INVALID_LAST_STATEMENT_EXIT_CODE = 10
# exit code we use if query script was canceled
QUERY_SCRIPT_CANCELED_EXIT_CODE = 11

# dataset pull
PULL_DATASET_MAX_THREADS = 10
PULL_DATASET_CHUNK_TIMEOUT = 3600
PULL_DATASET_SLEEP_INTERVAL = 0.1  # sleep time while waiting for chunk to be available
PULL_DATASET_CHECK_STATUS_INTERVAL = 20  # interval to check export status in Studio


def _raise_remote_error(error_message: str) -> NoReturn:
    raise DVCXError(f"Error from server: {error_message}")


class QueryResult(NamedTuple):
    dataset: Optional[DatasetRecord]
    version: Optional[int]
    output: str
    preview: Optional[list[dict]]


class DatasetRowsFetcher(NodesThreadPool):
    def __init__(
        self,
        metastore: "AbstractMetastore",
        warehouse: "AbstractWarehouse",
        remote_config: dict[str, Any],
        dataset_name: str,
        dataset_version: int,
        column_types: dict[str, SQLType],
        max_threads: int = PULL_DATASET_MAX_THREADS,
    ):
        super().__init__(max_threads)
        self._check_dependencies()
        self.metastore = metastore
        self.warehouse = warehouse
        self.dataset_name = dataset_name
        self.dataset_version = dataset_version
        self.column_types = column_types
        self.last_status_check: Optional[float] = None

        self.studio_client = StudioClient(
            remote_config["url"], remote_config["username"], remote_config["token"]
        )

    def done_task(self, done):
        for task in done:
            task.result()

    def _check_dependencies(self) -> None:
        try:
            import lz4.frame  # noqa: F401
            import numpy  # noqa: F401
            import pandas  # noqa: F401
            import pyarrow  # noqa: F401
        except ImportError as exc:
            raise Exception(
                f"Missing dependency: {exc.name}\n"
                "To install run:\n"
                "\tpip install 'dvcx[remote]'"
            ) from None

    def should_check_for_status(self) -> bool:
        if not self.last_status_check:
            return True
        return time.time() - self.last_status_check > PULL_DATASET_CHECK_STATUS_INTERVAL

    def check_for_status(self) -> None:
        """
        Method that checks export status in Studio and raises Exception if export
        failed or was removed.
        Checks are done every PULL_DATASET_CHECK_STATUS_INTERVAL seconds
        """
        export_status_response = self.studio_client.dataset_export_status(
            self.dataset_name, self.dataset_version
        )
        if not export_status_response.ok:
            _raise_remote_error(export_status_response.message)

        export_status = export_status_response.data["status"]  # type: ignore [index]

        if export_status == "failed":
            _raise_remote_error("Dataset export failed in Studio")
        if export_status == "removed":
            _raise_remote_error("Dataset export removed in Studio")

        self.last_status_check = time.time()

    def fix_columns(self, df) -> None:
        import pandas as pd

        """
        Method that does various column decoding or parsing, depending on a type
        before inserting into DB
        """
        # we get dataframe from parquet export files where datetimes are serialized
        # as timestamps so we need to parse it back to datetime objects
        for c in [c for c, t in self.column_types.items() if t == DateTime]:
            df[c] = pd.to_datetime(df[c], unit="s")

        # strings are represented as binaries in parquet export so need to
        # decode it back to strings
        for c in [c for c, t in self.column_types.items() if t == String]:
            df[c] = df[c].str.decode("utf-8")

    def do_task(self, urls):
        import lz4.frame
        import pandas as pd

        metastore = self.metastore.clone()  # metastore is not thread safe
        warehouse = self.warehouse.clone()  # warehouse is not thread safe
        dataset = metastore.get_dataset(self.dataset_name)

        while urls:
            for url in urls:
                if self.should_check_for_status():
                    self.check_for_status()

                r = requests.get(url, timeout=PULL_DATASET_CHUNK_TIMEOUT)
                if r.status_code == 404:
                    time.sleep(PULL_DATASET_SLEEP_INTERVAL)
                    # moving to the next url
                    continue

                r.raise_for_status()

                df = pd.read_parquet(io.BytesIO(lz4.frame.decompress(r.content)))

                self.fix_columns(df)

                # id will be autogenerated in DB
                df = df.drop("id", axis=1)

                inserted = warehouse.insert_dataset_rows(
                    df, dataset, self.dataset_version
                )
                self.increase_counter(inserted)  # type: ignore [arg-type]
                urls.remove(url)


@dataclass
class NodeGroup:
    """Class for a group of nodes from the same source"""

    listing: Listing
    sources: list[DataSource]

    # The source path within the bucket
    # (not including the bucket name or s3:// prefix)
    source_path: str = ""
    is_edvcx: bool = False
    dataset_name: Optional[str] = None
    dataset_version: Optional[int] = None
    instantiated_nodes: Optional[list[NodeWithPath]] = None

    @property
    def is_dataset(self) -> bool:
        return bool(self.dataset_name)

    def iternodes(self, recursive: bool = False):
        for src in self.sources:
            if recursive and src.is_container():
                for nwp in src.find():
                    yield nwp.n
            else:
                yield src.node

    def download(self, recursive: bool = False, pbar=None) -> None:
        """
        Download this node group to cache.
        """
        if self.sources:
            self.listing.client.fetch_nodes(
                self.iternodes(recursive), shared_progress_bar=pbar
            )


def check_output_dataset_file(
    output: str,
    force: bool = False,
    dataset_filename: Optional[str] = None,
    skip_check_edvcx: bool = False,
) -> str:
    """
    Checks the dataset filename for existence or if it should be force-overwritten.
    """
    dataset_file = (
        dataset_filename if dataset_filename else output + DATASET_FILE_SUFFIX
    )
    if not skip_check_edvcx:
        if os.path.exists(dataset_file):
            if force:
                os.remove(dataset_file)
            else:
                raise RuntimeError(
                    f"Output dataset file already exists: {dataset_file}"
                )
    return dataset_file


def parse_edvcx_file(filename: str) -> list[dict[str, Any]]:
    with open(filename, encoding="utf-8") as f:
        contents = yaml.safe_load(f)

    if not isinstance(contents, list):
        contents = [contents]

    for entry in contents:
        if not isinstance(entry, dict):
            raise ValueError(
                "Failed parsing EDVCX file, "
                "each data source entry must be a dictionary"
            )
        if "data-source" not in entry or "files" not in entry:
            raise ValueError(
                "Failed parsing EDVCX file, "
                "each data source entry must contain the "
                '"data-source" and "files" keys'
            )

    return contents


def prepare_output_for_cp(
    node_groups: list[NodeGroup],
    output: str,
    force: bool = False,
    edvcx_only: bool = False,
    no_edvcx_file: bool = False,
) -> tuple[bool, Optional[str]]:
    total_node_count = 0
    for node_group in node_groups:
        if not node_group.sources:
            raise FileNotFoundError(
                f"No such file or directory: {node_group.source_path}"
            )
        total_node_count += len(node_group.sources)

    always_copy_dir_contents = False
    copy_to_filename = None

    if edvcx_only:
        return always_copy_dir_contents, copy_to_filename

    if not os.path.isdir(output):
        if all(n.is_dataset for n in node_groups):
            os.mkdir(output)
        elif total_node_count == 1:
            first_source = node_groups[0].sources[0]
            if first_source.is_container():
                if os.path.exists(output):
                    if force:
                        os.remove(output)
                    else:
                        raise FileExistsError(f"Path already exists: {output}")
                always_copy_dir_contents = True
                os.mkdir(output)
            else:  # Is a File
                if os.path.exists(output):
                    if force:
                        os.remove(output)
                    else:
                        raise FileExistsError(f"Path already exists: {output}")
                copy_to_filename = output
        else:
            raise FileNotFoundError(f"Is not a directory: {output}")

    if copy_to_filename and not no_edvcx_file:
        raise RuntimeError("File to file cp not supported with .edvcx files!")

    return always_copy_dir_contents, copy_to_filename


def collect_nodes_for_cp(
    node_groups: Iterable[NodeGroup],
    recursive: bool = False,
) -> tuple[int, int]:
    total_size: int = 0
    total_files: int = 0

    # Collect all sources to process
    for node_group in node_groups:
        listing: Listing = node_group.listing
        valid_sources: list[DataSource] = []
        for dsrc in node_group.sources:
            if dsrc.is_single_object():
                total_size += dsrc.node.size
                total_files += 1
                valid_sources.append(dsrc)
            else:
                node = dsrc.node
                if not recursive:
                    print(f"{node.full_path} is a directory (not copied).")
                    continue
                add_size, add_files = listing.du(node, count_files=True)
                total_size += add_size
                total_files += add_files
                valid_sources.append(dsrc)

        node_group.sources = valid_sources

    return total_size, total_files


def get_download_bar(bar_format: str, total_size: int):
    return tqdm(
        desc="Downloading files: ",
        unit="B",
        bar_format=bar_format,
        unit_scale=True,
        unit_divisor=1000,
        total=total_size,
    )


def instantiate_node_groups(
    node_groups: Iterable[NodeGroup],
    output: str,
    bar_format: str,
    total_files: int,
    force: bool = False,
    recursive: bool = False,
    virtual_only: bool = False,
    always_copy_dir_contents: bool = False,
    copy_to_filename: Optional[str] = None,
) -> None:
    instantiate_progress_bar = (
        None
        if virtual_only
        else tqdm(
            desc=f"Instantiating {output}: ",
            unit=" f",
            bar_format=bar_format,
            unit_scale=True,
            unit_divisor=1000,
            total=total_files,
        )
    )

    output_dir = output
    if copy_to_filename:
        output_dir = os.path.dirname(output)
        if not output_dir:
            output_dir = "."

    # Instantiate these nodes
    for node_group in node_groups:
        if not node_group.sources:
            continue
        listing: Listing = node_group.listing
        source_path: str = node_group.source_path

        copy_dir_contents = always_copy_dir_contents or source_path.endswith("/")
        instantiated_nodes = listing.collect_nodes_to_instantiate(
            node_group.sources,
            copy_to_filename,
            recursive,
            copy_dir_contents,
            source_path,
            node_group.is_edvcx,
            node_group.is_dataset,
        )
        if not virtual_only:
            listing.instantiate_nodes(
                instantiated_nodes,
                output_dir,
                total_files,
                force=force,
                shared_progress_bar=instantiate_progress_bar,
            )
        node_group.instantiated_nodes = instantiated_nodes
    if instantiate_progress_bar:
        instantiate_progress_bar.close()


def compute_metafile_data(node_groups) -> list[dict[str, Any]]:
    metafile_data = []
    for node_group in node_groups:
        if not node_group.sources:
            continue
        listing: Listing = node_group.listing
        source_path: str = node_group.source_path
        metafile_group = {
            "data-source": (
                listing.storage.to_dict(source_path)
                if not node_group.is_dataset
                else {"uri": listing.warehouse.uri}
            ),
            "files": [],
        }
        for node in node_group.instantiated_nodes:
            if not node.n.is_dir:
                metafile_group["files"].append(node.get_metafile_data())
        if metafile_group["files"]:
            metafile_data.append(metafile_group)

    return metafile_data


def find_column_to_str(  # noqa: PLR0911
    row: tuple[Any, ...], field_lookup: dict[str, int], src: DataSource, column: str
) -> str:
    if column == "du":
        return str(
            src.listing.du(
                {
                    f: row[field_lookup[f]]
                    for f in ["dir_type", "size", "parent", "name"]
                }
            )[0]
        )
    if column == "name":
        return row[field_lookup["name"]] or ""
    if column == "owner":
        return row[field_lookup["owner_name"]] or ""
    if column == "path":
        is_dir = row[field_lookup["dir_type"]] == DirType.DIR
        parent = row[field_lookup["parent"]]
        name = row[field_lookup["name"]]
        path = f"{parent}/{name}" if parent else name
        if is_dir and path:
            full_path = path + "/"
        else:
            full_path = path
        return src.get_node_full_path_from_path(full_path)
    if column == "size":
        return str(row[field_lookup["size"]])
    if column == "type":
        dt = row[field_lookup["dir_type"]]
        if dt == DirType.DIR:
            return "d"
        elif dt == DirType.FILE:
            return "f"
        elif dt == DirType.TAR_ARCHIVE:
            return "t"
        # Unknown - this only happens if a type was added elsewhere but not here
        return "u"
    return ""


class Catalog:
    def __init__(
        self,
        id_generator: "AbstractIDGenerator",
        metastore: "AbstractMetastore",
        warehouse: "AbstractWarehouse",
        cache_dir=None,
        tmp_dir=None,
        client_config: Optional[dict[str, Any]] = None,
    ):
        dvcx_dir = DVCXDir(cache=cache_dir, tmp=tmp_dir)
        dvcx_dir.init()
        self.id_generator = id_generator
        self.metastore = metastore
        self.warehouse = warehouse
        self.cache = DVCXCache(dvcx_dir.cache, dvcx_dir.tmp)
        self.client_config = client_config if client_config is not None else {}
        self._init_params = {
            "cache_dir": cache_dir,
            "tmp_dir": tmp_dir,
        }

    def get_init_params(self) -> dict[str, Any]:
        return {
            **self._init_params,
            "client_config": self.client_config,
        }

    def copy(self, cache=True, db=True):
        result = copy(self)
        if not db:
            result.id_generator = None
            result.metastore = None
            result.warehouse = None
        return result

    @classmethod
    def generate_query_dataset_name(cls) -> str:
        return f"{QUERY_DATASET_NAME_PREFIX}_{uuid4().hex}"

    def compile_query_script(self, script: str, save=False) -> str:
        wrapper_function = "query_wrapper_print"
        if save:
            wrapper_function = "query_wrapper_save"

        code_ast = ast.parse(script)
        if code_ast.body:
            last_expr = code_ast.body[-1]
            if isinstance(last_expr, Expr):
                new_expressions = [
                    Import(names=[alias(name="dvcx.query.dataset", asname=None)]),
                    Expr(
                        value=Call(
                            func=Attribute(
                                value=Attribute(
                                    value=Attribute(
                                        value=Name(id="dvcx", ctx=Load()),
                                        attr="query",
                                        ctx=Load(),
                                    ),
                                    attr="dataset",
                                    ctx=Load(),
                                ),
                                attr=wrapper_function,
                                ctx=Load(),
                            ),
                            args=[last_expr],
                            keywords=[],
                        )
                    ),
                ]
                code_ast.body[-1:] = new_expressions
            else:
                raise Exception("Last line in a script was not an expression")

        return ast.unparse(code_ast)

    def add_storage(self, source: str) -> None:
        path = LocalFileSystem._strip_protocol(source)
        if not os.path.isdir(path):
            raise RuntimeError(f"{path} is not a directory")
        uri = StorageURI(Path(path).resolve().as_uri())
        print(f"Registering storage {uri}")
        self.metastore.create_storage_if_not_registered(uri)

    def parse_url(self, uri: str, **config: Any) -> tuple[Client, str]:
        config = config or self.client_config
        return Client.parse_url(uri, self.metastore, self.cache, **config)

    def get_client(self, uri: StorageURI, **config: Any) -> Client:
        """
        Return the client corresponding to the given source `uri`.
        """
        config = config or self.client_config
        cls = Client.get_implementation(uri)
        return cls.from_source(uri, self.cache, **config)

    def enlist_source(
        self,
        source: str,
        ttl: int,
        force_update=False,
        skip_indexing=False,
        client_config=None,
        index_processors: Optional[list[IndexingFormat]] = None,
    ) -> tuple[Listing, str]:
        if force_update and skip_indexing:
            raise ValueError(
                "Both force_update and skip_indexing flags"
                " cannot be True at the same time"
            )

        client_config = client_config or self.client_config
        client, path = self.parse_url(source, **client_config)
        prefix = posixpath.dirname(path)
        source_metastore = self.metastore.clone(client.uri)
        source_warehouse = self.warehouse.clone(client.uri)

        partial_id: Optional[int]
        if skip_indexing:
            source_metastore.create_storage_if_not_registered(client.uri)
            storage = source_metastore.get_storage(client.uri)
            source_metastore.init_partial_id(client.uri)
            partial_id = source_metastore.get_next_partial_id(client.uri)

            source_metastore = self.metastore.clone(
                uri=client.uri, partial_id=partial_id
            )
            source_metastore.init(client.uri, partial_id)

            source_warehouse = self.warehouse.clone(
                uri=client.uri, partial_id=partial_id
            )
            source_warehouse.init_db(client.uri, partial_id)

            return (
                Listing(storage, source_metastore, source_warehouse, client),
                path,
            )

        (
            storage,
            need_index,
            in_progress,
            partial_id,
        ) = source_metastore.register_storage_for_indexing(
            client.uri, force_update, prefix
        )
        if in_progress:
            raise PendingIndexingError(f"Pending indexing operation: uri={storage.uri}")

        if not need_index:
            assert partial_id is not None
            source_metastore = self.metastore.clone(
                uri=client.uri, partial_id=partial_id
            )
            source_warehouse = self.warehouse.clone(
                uri=client.uri, partial_id=partial_id
            )
            lst = Listing(storage, source_metastore, source_warehouse, client)
            logger.debug(  # type: ignore[unreachable]
                f"Using cached listing {storage.uri}."
                + f" Valid till: {storage.expires_to_local}"
            )
            # Listing has to have correct version of data storage
            # initialized with correct Storage
            return lst, path

        source_metastore.init_partial_id(client.uri)
        partial_id = source_metastore.get_next_partial_id(client.uri)

        source_metastore.init(client.uri, partial_id)
        source_metastore = self.metastore.clone(uri=client.uri, partial_id=partial_id)

        source_warehouse.init_db(client.uri, partial_id)
        source_warehouse = self.warehouse.clone(uri=client.uri, partial_id=partial_id)

        lst = Listing(storage, source_metastore, source_warehouse, client)

        try:
            lst.fetch(prefix)

            # Apply index processing before marking storage as indexed.
            if index_processors:
                apply_processors(lst, path, index_processors)

            source_metastore.mark_storage_indexed(
                storage.uri,
                Status.PARTIAL if prefix else Status.COMPLETE,
                ttl,
                prefix=prefix,
                partial_id=partial_id,
            )
        except InconsistentSignalType as e:
            # handle all custom errors here which messages we want to show
            # directly to the user (user mistake generated error)
            source_metastore.mark_storage_indexed(
                storage.uri,
                Status.FAILED,
                ttl,
                prefix=prefix,
                error_message=str(e),
                error_stack=traceback.format_exc(),
            )
            raise
        except ClientError as e:
            # for handling cloud errors
            error_message = INDEX_INTERNAL_ERROR_MESSAGE
            if e.error_code in ["InvalidAccessKeyId", "SignatureDoesNotMatch"]:
                error_message = "Invalid cloud credentials"

            source_metastore.mark_storage_indexed(
                storage.uri,
                Status.FAILED,
                ttl,
                prefix=prefix,
                error_message=error_message,
                error_stack=traceback.format_exc(),
            )
            raise
        except:
            source_metastore.mark_storage_indexed(
                storage.uri,
                Status.FAILED,
                ttl,
                prefix=prefix,
                error_message=INDEX_INTERNAL_ERROR_MESSAGE,
                error_stack=traceback.format_exc(),
            )
            raise

        lst.storage = storage

        return lst, path

    def enlist_sources(
        self,
        sources: list[str],
        ttl: int,
        update: bool,
        skip_indexing=False,
        client_config=None,
        index_processors: Optional[list[IndexingFormat]] = None,
        only_index=False,
    ) -> Optional[list["DataSource"]]:
        enlisted_sources = []
        for src in sources:  # Opt: parallel
            listing, file_path = self.enlist_source(
                src,
                ttl,
                update,
                skip_indexing=skip_indexing,
                client_config=client_config or self.client_config,
                index_processors=index_processors,
            )
            enlisted_sources.append((listing, file_path))

        if only_index:
            # sometimes we don't really need listing result (e.g on indexing process)
            # so this is to improve performance
            return None

        dsrc_all = []
        for listing, file_path in enlisted_sources:
            nodes = listing.expand_path(file_path)
            dir_only = file_path.endswith("/")
            for node in nodes:
                dsrc_all.append(DataSource(listing, node, dir_only))

        return dsrc_all

    def enlist_sources_grouped(
        self,
        sources: list[str],
        ttl: int,
        update: bool,
        no_glob: bool = False,
        client_config=None,
    ) -> list[NodeGroup]:
        def _ds_row_to_node(dr: DatasetRow) -> Node:
            d = asdict(dr)  # type: ignore [arg-type]
            del d["source"]
            del d["custom"]
            return Node(**d)

        enlisted_sources: list[tuple[bool, bool, Any]] = []
        client_config = client_config or self.client_config
        for src in sources:  # Opt: parallel
            if src.endswith(DATASET_FILE_SUFFIX) and os.path.isfile(src):
                # TODO: Also allow using EDVCX files from cloud locations?
                edvcx_data = parse_edvcx_file(src)
                indexed_sources = []
                for ds in edvcx_data:
                    listing, source_path = self.enlist_source(
                        ds["data-source"]["uri"],
                        ttl,
                        update,
                        client_config=client_config,
                    )
                    paths = dvcx_paths_join(
                        source_path, (f["name"] for f in ds["files"])
                    )
                    indexed_sources.append((listing, source_path, paths))
                enlisted_sources.append((True, False, indexed_sources))
            elif src.startswith("ds://"):
                ds_name, ds_version = parse_dataset_uri(src)
                dataset = self.get_dataset(ds_name)
                if not ds_version:
                    ds_version = dataset.latest_version
                dataset_sources = self.warehouse.get_dataset_sources(
                    dataset,
                    ds_version,
                )
                indexed_sources = []
                for source in dataset_sources:
                    client = self.get_client(source, **client_config)
                    uri = client.uri
                    ms = self.metastore.clone(uri, None)
                    st = self.warehouse.clone(uri, None)
                    listing = Listing(
                        None,  # type: ignore [arg-type]
                        ms,
                        st,
                        client,
                    )
                    rows = st.get_dataset_rows(
                        dataset,
                        ds_version,
                        limit=None,
                        source=source,
                    )
                    indexed_sources.append(
                        (
                            listing,
                            source,
                            rows,
                            ds_name,
                            ds_version,
                        )  # type: ignore [arg-type]
                    )

                enlisted_sources.append((False, True, indexed_sources))
            else:
                listing, source_path = self.enlist_source(
                    src, ttl, update, client_config=client_config
                )
                enlisted_sources.append((False, False, (listing, source_path)))

        node_groups = []
        for is_dvcx, is_dataset, payload in enlisted_sources:  # Opt: parallel
            if is_dataset:
                for (
                    listing,
                    source_path,
                    dataset_rows,
                    dataset_name,
                    dataset_version,
                ) in payload:
                    nodes = [_ds_row_to_node(row) for row in dataset_rows]
                    dsrc = [DataSource(listing, node) for node in nodes]
                    node_groups.append(
                        NodeGroup(
                            listing,
                            dsrc,
                            source_path,
                            dataset_name=dataset_name,
                            dataset_version=dataset_version,
                        )
                    )
            elif is_dvcx:
                for listing, source_path, paths in payload:
                    dsrc = [DataSource(listing, listing.resolve_path(p)) for p in paths]
                    node_groups.append(
                        NodeGroup(listing, dsrc, source_path, is_edvcx=True)
                    )
            else:
                listing, source_path = payload
                as_container = source_path.endswith("/")
                if no_glob:
                    dsrc = [
                        DataSource(
                            listing, listing.resolve_path(source_path), as_container
                        )
                    ]
                else:
                    dsrc = [
                        DataSource(listing, n, as_container)
                        for n in listing.expand_path(source_path)
                    ]
                node_groups.append(NodeGroup(listing, dsrc, source_path))

        return node_groups

    def unlist_source(self, uri: StorageURI) -> None:
        self.metastore.clone(uri=uri).mark_storage_not_indexed(uri)

    def storage_stats(self, uri: StorageURI) -> Optional[StorageStats]:
        """
        Returns tuple with storage stats: total number of rows and total dataset size.
        """
        partial_id = self.metastore.get_last_partial_id(uri)
        if not partial_id:
            return None
        num_objects, size = self.warehouse.storage_stats(uri, partial_id)
        return StorageStats(
            num_objects=num_objects,
            size=size,
        )

    def _get_nodes(self, sources: Iterable[str], client_config) -> list:
        """Gets list of nodes based on sources"""
        nodes = []
        for source in sources:
            client, path = self.parse_url(source, **client_config)
            uri = client.uri
            partial_id = self.metastore.get_valid_partial_id(uri, path)
            nodes.append(self.warehouse.nodes_table(uri, partial_id))

        return nodes

    def create_dataset(
        self,
        name: str,
        version: Optional[int] = None,
        query_script: str = "",
        create_rows: Optional[bool] = True,
        custom_columns: Sequence[Column] = (),
        validate_version: Optional[bool] = True,
    ) -> "DatasetRecord":
        """
        Creates new dataset of a specific version.
        If dataset is not yet created, it will create it with version 1
        If version is None, then next unused version is created.
        If version is given, then it must be an unused version number.
        """
        default_version = 1
        try:
            dataset = self.get_dataset(name)
            default_version = dataset.next_version
        except DatasetNotFoundError:
            custom_column_types = {
                c.name: c.type.to_dict()
                for c in list(custom_columns)
                if isinstance(c.type, SQLType)
            }
            dataset = self.metastore.create_dataset(
                name,
                query_script=query_script,
                custom_column_types=custom_column_types,
                ignore_if_exists=True,
            )

        version = version or default_version

        if dataset.has_version(version):
            raise DatasetInvalidVersionError(
                f"Version {version} already exists in dataset {name}"
            )

        if validate_version and not dataset.is_valid_next_version(version):
            raise DatasetInvalidVersionError(
                f"Version {version} must be higher than the current latest one"
            )

        dataset = self.create_new_dataset_version(
            dataset,
            version,
            query_script=query_script,
            create_rows_table=create_rows,
            custom_columns=custom_columns,
        )

        return dataset

    def create_new_dataset_version(
        self,
        dataset: DatasetRecord,
        version: int,
        sources="",
        query_script="",
        error_message="",
        error_stack="",
        script_output="",
        create_rows_table=True,
        custom_columns: Sequence[Column] = (),
    ) -> DatasetRecord:
        """
        Creates dataset version if it doesn't exist.
        If create_rows is False, dataset rows table will not be created
        """
        custom_column_types = {
            c.name: c.type.to_dict()
            for c in self.warehouse.schema.dataset_row_cls.default_columns()
            + list(custom_columns)
            if isinstance(c.type, SQLType)
        }

        dataset = self.metastore.create_dataset_version(
            dataset,
            version,
            status=DatasetStatus.PENDING,
            sources=sources,
            query_script=query_script,
            error_message=error_message,
            error_stack=error_stack,
            script_output=script_output,
            custom_column_types=custom_column_types,
            ignore_if_exists=True,
        )

        if create_rows_table:
            table_name = self.warehouse.dataset_table_name(dataset.name, version)
            self.warehouse.create_dataset_rows_table(
                table_name, custom_columns=custom_columns
            )

        return dataset

    def update_dataset(
        self, dataset: DatasetRecord, conn=None, **kwargs
    ) -> DatasetRecord:
        """Updates dataset fields."""
        old_name = None
        new_name = None
        if "name" in kwargs and kwargs["name"] != dataset.name:
            old_name = dataset.name
            new_name = kwargs["name"]

        dataset = self.metastore.update_dataset(dataset, conn=conn, **kwargs)

        if old_name and new_name:
            # updating name must result in updating dataset table names as well
            for version in [v.version for v in dataset.versions]:
                self.warehouse.rename_dataset_table(
                    old_name,
                    new_name,
                    old_version=version,
                    new_version=version,
                )

        return dataset

    def remove_dataset_version(
        self, dataset: DatasetRecord, version: int, drop_rows: Optional[bool] = True
    ) -> None:
        """
        Deletes one single dataset version.
        If it was last version, it removes dataset completely
        """
        if not dataset.has_version(version):
            return
        dataset = self.metastore.remove_dataset_version(dataset, version)
        if drop_rows:
            self.warehouse.drop_dataset_rows_table(dataset, version)

    def cleanup_temp_tables(self, names: Iterable[str]) -> None:
        """
        Drop tables created temporarily when processing datasets.

        This should be implemented even if temporary tables are used to
        ensure that they are cleaned up as soon as they are no longer
        needed. When running the same `DatasetQuery` multiple times we
        may use the same temporary table names.
        """
        self.warehouse.cleanup_temp_tables(names)
        self.id_generator.delete_uris(names)

    def create_dataset_from_sources(
        self,
        name: str,
        sources: list[str],
        client_config=None,
        recursive=False,
    ) -> DatasetRecord:
        if not sources:
            raise ValueError("Sources needs to be non empty list")

        from dvcx.query import DatasetQuery

        dataset_queries = []
        for source in sources:
            if source.startswith(DATASET_PREFIX):
                dq = DatasetQuery(
                    name=source[len(DATASET_PREFIX) :],
                    catalog=self,
                    client_config=client_config,
                )
            else:
                dq = DatasetQuery(
                    path=source,
                    catalog=self,
                    client_config=client_config,
                    recursive=recursive,
                )

            dataset_queries.append(dq)

        # create union of all dataset queries created from sources
        dq = functools.reduce(lambda ds1, ds2: ds1.union(ds2), dataset_queries)
        try:
            dq.save(name)
        except Exception:
            ds = self.get_dataset(name)
            self.metastore.update_dataset_status(
                ds,
                DatasetStatus.FAILED,
                version=ds.latest_version,
                error_message=DATASET_INTERNAL_ERROR_MESSAGE,
                error_stack=traceback.format_exc(),
            )
            self.metastore.update_dataset_version(
                ds.get_version(ds.latest_version),  # type: ignore[arg-type]
                sources="\n".join(sources),
            )
            raise

        ds = self.get_dataset(name)

        self.metastore.update_dataset_version(
            ds.get_version(ds.latest_version),  # type: ignore[arg-type]
            sources="\n".join(sources),
        )

        return self.get_dataset(name)

    def register_dataset(
        self,
        dataset: DatasetRecord,
        version: int,
        target_dataset: DatasetRecord,
        target_version: Optional[int] = None,
    ) -> DatasetRecord:
        """
        Registers dataset version of one dataset as dataset version of another
        one (it can be new version of existing one).
        It also removes original dataset version
        """
        target_version = target_version or target_dataset.next_version

        if not target_dataset.is_valid_next_version(target_version):
            raise DatasetInvalidVersionError(
                f"Version {target_version} must be higher than the current latest one"
            )

        dataset_version = dataset.get_version(version)
        if not dataset_version:
            raise ValueError(f"Dataset {dataset.name} does not have version {version}")

        if not dataset_version.is_final_status():
            raise ValueError("Cannot register dataset version in non final status")

        # copy dataset version
        target_dataset = self.metastore.create_dataset_version(
            target_dataset,
            target_version,
            sources=dataset_version.sources,
            status=dataset_version.status,
            query_script=dataset_version.query_script,
            error_message=dataset_version.error_message,
            error_stack=dataset_version.error_stack,
            script_output=dataset_version.script_output,
            created_at=dataset_version.created_at,
            finished_at=dataset_version.finished_at,
            custom_column_types=dataset_version.custom_column_types_serialized,
        )
        # to avoid re-creating rows table, we are just renaming it for a new version
        # of target dataset
        self.warehouse.rename_dataset_table(
            dataset.name,
            target_dataset.name,
            old_version=version,
            new_version=target_version,
        )
        self.metastore.update_dataset_dependency_source(
            dataset,
            version,
            new_source_dataset=target_dataset,
            new_source_dataset_version=target_version,
        )

        if dataset.id == target_dataset.id:
            # we are updating the same dataset so we need to refresh it to have newly
            # added version in step before
            dataset = self.get_dataset(dataset.name)

        self.remove_dataset_version(dataset, version, drop_rows=False)

        return self.get_dataset(target_dataset.name)

    def get_dataset(self, name: str) -> DatasetRecord:
        return self.metastore.get_dataset(name)

    def get_remote_dataset(self, name: str, *, remote_config=None) -> DatasetRecord:
        remote_config = remote_config or get_remote_config(
            read_config(DVCXDir.find().root), remote=""
        )
        studio_client = StudioClient(
            remote_config["url"], remote_config["username"], remote_config["token"]
        )

        info_response = studio_client.dataset_info(name)
        if not info_response.ok:
            _raise_remote_error(info_response.message)

        dataset_info = info_response.data
        assert isinstance(dataset_info, dict)
        return DatasetRecord.from_dict(dataset_info)

    def get_dataset_dependencies(
        self, name: str, version: int, indirect=False
    ) -> list[Optional[DatasetDependency]]:
        dataset = self.get_dataset(name)

        direct_dependencies = self.metastore.get_direct_dataset_dependencies(
            dataset, version
        )

        if not indirect:
            return direct_dependencies

        for d in direct_dependencies:
            if not d:
                # dependency has been removed
                continue
            if d.is_dataset:
                # only datasets can have dependencies
                d.dependencies = self.get_dataset_dependencies(
                    d.name, int(d.version), indirect=indirect
                )

        return direct_dependencies

    def ls_datasets(self) -> Iterator[DatasetRecord]:
        yield from self.metastore.list_datasets()

    def ls_dataset_rows(
        self, name: str, version: int, offset=None, limit=None, custom_columns=False
    ) -> Iterator[DatasetRow]:
        dataset = self.get_dataset(name)

        yield from self.warehouse.get_dataset_rows(
            dataset,
            version,
            offset=offset,
            limit=limit,
            custom_columns=custom_columns,
        )

    def signed_url(self, source: str, path: str, client_config=None) -> str:
        client_config = client_config or self.client_config
        client, _ = self.parse_url(source, **client_config)
        return client.url(path)

    def export_dataset_table(
        self,
        bucket_uri: str,
        name: str,
        version: int,
        client_config=None,
    ) -> list[str]:
        dataset = self.get_dataset(name)

        return self.warehouse.export_dataset_table(
            bucket_uri, dataset, version, client_config
        )

    def dataset_table_export_file_names(self, name: str, version: int) -> list[str]:
        dataset = self.get_dataset(name)
        return self.warehouse.dataset_table_export_file_names(dataset, version)

    def dataset_stats(self, name: str, version: int) -> DatasetStats:
        """
        Returns tuple with dataset stats: total number of rows and total dataset size.
        """
        dataset = self.get_dataset(name)
        num_objects, size = self.warehouse.dataset_stats(dataset, version)
        return DatasetStats(
            num_objects=num_objects,
            size=size,
        )

    def remove_dataset(
        self,
        name: str,
        version: Optional[int] = None,
        force: Optional[bool] = False,
    ):
        dataset = self.get_dataset(name)
        if not version and not force:
            raise ValueError(f"Missing dataset version from input for dataset {name}")
        if version and not dataset.has_version(version):
            raise DatasetInvalidVersionError(
                f"Dataset {name} doesn't have version {version}"
            )

        if version:
            self.remove_dataset_version(dataset, version)
            return

        for version in dataset.versions.copy():  # type: ignore [assignment, union-attr]
            self.remove_dataset_version(
                dataset,
                version.version,  # type: ignore [union-attr]
            )

    def edit_dataset(
        self,
        name: str,
        new_name: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[list[str]] = None,
    ) -> DatasetRecord:
        update_data = {}
        if new_name:
            update_data["name"] = new_name
        if description is not None:
            update_data["description"] = description
        if labels is not None:
            update_data["labels"] = labels  # type: ignore[assignment]

        dataset = self.get_dataset(name)
        return self.update_dataset(dataset, **update_data)

    def merge_datasets(
        self,
        src: DatasetRecord,
        dst: DatasetRecord,
        src_version: int,
        dst_version: Optional[int] = None,
    ) -> DatasetRecord:
        """
        Merges records from source to destination dataset.
        It will create new version
        of a dataset with records merged from old version and the source, unless
        existing version is specified for destination in which case it must
        be in non final status as datasets are immutable
        """
        if (
            dst_version
            and not dst.is_valid_next_version(dst_version)
            and dst.get_version(dst_version).is_final_status()
        ):
            raise DatasetInvalidVersionError(
                f"Version {dst_version} must be higher than the current latest one"
            )

        src_dep = self.get_dataset_dependencies(src.name, src_version)
        dst_dep = self.get_dataset_dependencies(
            dst.name,
            dst.latest_version,  # type: ignore[arg-type]
        )

        if dst.has_version(dst_version):  # type: ignore[arg-type]
            # case where we don't create new version, but append to the existing one
            self.warehouse.merge_dataset_rows(
                src,
                dst,
                src_version,
                dst_version=dst_version,  # type: ignore[arg-type]
            )
            merged_custom_column_types = {
                **src.custom_column_types_serialized,
                **dst.custom_column_types_serialized,
            }
            self.update_dataset(dst, custom_column_types=merged_custom_column_types)
            self.metastore.update_dataset_version(
                dst.get_version(dst_version),  # type: ignore[arg-type]
                custom_column_types=merged_custom_column_types,
            )
            for dep in src_dep:
                if dep and dep not in dst_dep:
                    self.metastore.add_dependency(
                        dep,
                        dst.name,
                        dst_version,  # type: ignore[arg-type]
                    )
        else:
            # case where we create new version of merged results
            src_dr = self.warehouse.dataset_rows(src, src_version)
            dst_dr = self.warehouse.dataset_rows(dst)

            merge_result_columns = list(
                {
                    c.name: c for c in list(src_dr.table.c) + list(dst_dr.table.c)
                }.values()
            )
            custom_columns = [
                c
                for c in merge_result_columns
                if c.name not in DATASET_CORE_COLUMN_NAMES
            ]

            dst_version = dst_version or dst.next_version
            dst = self.create_new_dataset_version(
                dst, dst_version, custom_columns=custom_columns
            )
            self.warehouse.merge_dataset_rows(
                src,
                dst,
                src_version,
                dst_version,
            )
            for dep in set(src_dep + dst_dep):
                if dep:
                    self.metastore.add_dependency(dep, dst.name, dst_version)

        return dst

    def open_object(self, row: DatasetRow, use_cache: bool = True, **config: Any):
        config = config or self.client_config
        client = self.get_client(row.source, **config)
        return client.open_object(row.as_uid(), use_cache=use_cache)

    def ls(
        self,
        sources: list[str],
        fields: Iterable[str],
        ttl=TTL_INT,
        update=False,
        skip_indexing=False,
        *,
        client_config=None,
    ) -> Iterator[tuple[DataSource, Iterable[tuple]]]:
        data_sources = self.enlist_sources(
            sources,
            ttl,
            update,
            skip_indexing=skip_indexing,
            client_config=client_config or self.client_config,
        )

        for source in data_sources:  # type: ignore [union-attr]
            yield source, source.ls(fields)

    def ls_storage_uris(self) -> Iterator[str]:
        yield from self.metastore.get_all_storage_uris()

    def get_storage(self, uri: StorageURI) -> Storage:
        return self.metastore.get_storage(uri)

    def ls_storages(self) -> list[Storage]:
        return self.metastore.list_storages()

    def pull_dataset(  # noqa: C901, PLR0911
        self,
        dataset_uri: str,
        output: Optional[str] = None,
        no_cp: bool = False,
        force: bool = False,
        edvcx: bool = False,
        edvcx_file: Optional[str] = None,
        *,
        client_config=None,
        remote_config=None,
    ) -> None:
        # TODO add progress bar https://github.com/iterative/dvcx/issues/750
        # TODO copy correct remote dates https://github.com/iterative/dvcx/issues/new
        # TODO compare dataset stats on remote vs local pull to assert it's ok
        def _instantiate_dataset():
            if no_cp:
                return
            self.cp(
                [dataset_uri],
                output,
                force=force,
                no_edvcx_file=not edvcx,
                edvcx_file=edvcx_file,
                client_config=client_config,
            )
            print(f"Dataset {dataset_uri} instantiated locally to {output}")

        if not output and not no_cp:
            raise ValueError("Please provide output directory for instantiation")

        client_config = client_config or self.client_config
        remote_config = remote_config or get_remote_config(
            read_config(DVCXDir.find().root), remote=""
        )

        studio_client = StudioClient(
            remote_config["url"], remote_config["username"], remote_config["token"]
        )

        try:
            remote_dataset_name, version = parse_dataset_uri(dataset_uri)
        except Exception as e:
            raise DVCXError("Error when parsing dataset uri") from e

        dataset = None
        try:
            dataset = self.get_dataset(remote_dataset_name)
        except DatasetNotFoundError:
            # we will create new one if it doesn't exist
            pass

        remote_dataset = self.get_remote_dataset(
            remote_dataset_name, remote_config=remote_config
        )
        # if version is not specified in uri, take the latest one
        if not version:
            version = remote_dataset.latest_version
            print(f"Version not specified, pulling the latest one (v{version})")
            # updating dataset uri with latest version
            dataset_uri = create_dataset_uri(remote_dataset_name, version)

        assert version

        if dataset and dataset.has_version(version):
            print(f"Local copy of dataset {dataset_uri} already present")
            _instantiate_dataset()
            return

        try:
            remote_dataset_version = remote_dataset.get_version(version)
        except (ValueError, StopIteration) as exc:
            raise DVCXError(
                f"Dataset {remote_dataset_name} doesn't have version {version}"
                " on server"
            ) from exc

        stats_response = studio_client.dataset_stats(remote_dataset_name, version)
        if not stats_response.ok:
            _raise_remote_error(stats_response.message)
        dataset_stats = stats_response.data

        dataset_save_progress_bar = tqdm(
            desc=f"Saving dataset {dataset_uri} locally: ",
            unit=" rows",
            unit_scale=True,
            unit_divisor=1000,
            total=dataset_stats.num_objects,  # type: ignore [union-attr]
        )

        custom_column_types = DatasetRecord.parse_custom_column_types(
            remote_dataset_version.custom_column_types,
        )
        custom_columns = [
            sa.Column(c_name, c_type)
            for c_name, c_type in custom_column_types.items()
            if c_name not in DATASET_CORE_COLUMN_NAMES
        ]

        # creating new dataset (version) locally
        dataset = self.create_dataset(
            remote_dataset_name,
            version,
            query_script=remote_dataset_version.query_script,
            create_rows=True,
            custom_columns=custom_columns,
            validate_version=False,
        )

        # asking remote to export dataset rows table to s3 and to return signed
        # urls of exported parts, which are in parquet format
        export_response = studio_client.export_dataset_table(
            remote_dataset_name, version
        )
        if not export_response.ok:
            _raise_remote_error(export_response.message)

        signed_urls = export_response.data

        if signed_urls:
            shuffle(signed_urls)

            rows_fetcher = DatasetRowsFetcher(
                self.metastore.clone(),
                self.warehouse.clone(),
                remote_config,
                dataset.name,
                version,
                custom_column_types,
            )
            try:
                rows_fetcher.run(
                    chunk(
                        signed_urls,
                        math.ceil(len(signed_urls) / PULL_DATASET_MAX_THREADS),
                    ),
                    dataset_save_progress_bar,
                )
            except:
                self.remove_dataset(dataset.name, version)
                raise

        dataset = self.metastore.update_dataset_status(
            dataset,
            DatasetStatus.COMPLETE,
            version=version,
            error_message=remote_dataset.error_message,
            error_stack=remote_dataset.error_stack,
            script_output=remote_dataset.error_stack,
        )

        dataset_save_progress_bar.close()
        print(f"Dataset {dataset_uri} saved locally")

        _instantiate_dataset()

    def clone(
        self,
        sources: list[str],
        output: str,
        force: bool = False,
        update: bool = False,
        recursive: bool = False,
        no_glob: bool = False,
        no_cp: bool = False,
        edvcx: bool = False,
        edvcx_file: Optional[str] = None,
        ttl: int = TTL_INT,
        *,
        client_config=None,
    ) -> None:
        """
        This command takes cloud path(s) and duplicates files and folders in
        them into the dataset folder.
        It also adds those files to a dataset in database, which is
        created if doesn't exist yet
        Optionally, it creates a .edvcx file
        """
        if not no_cp or edvcx:
            self.cp(
                sources,
                output,
                force=force,
                update=update,
                recursive=recursive,
                no_glob=no_glob,
                edvcx_only=no_cp,
                no_edvcx_file=not edvcx,
                edvcx_file=edvcx_file,
                ttl=ttl,
                client_config=client_config,
            )
        else:
            # since we don't call cp command, which does listing implicitly,
            # it needs to be done here
            self.enlist_sources(
                sources,
                ttl,
                update,
                client_config=client_config or self.client_config,
            )

        self.create_dataset_from_sources(
            output, sources, client_config=client_config, recursive=recursive
        )

    def apply_udf(
        self,
        udf_location: str,
        source: str,
        target_name: str,
        parallel: Optional[int] = None,
        params: Optional[str] = None,
    ):
        from dvcx.query import DatasetQuery

        if source.startswith(DATASET_PREFIX):
            ds = DatasetQuery(name=source[len(DATASET_PREFIX) :], catalog=self)
        else:
            ds = DatasetQuery(path=source, catalog=self)
        udf = import_object(udf_location)
        if params:
            args, kwargs = parse_params_string(params)
            udf = udf(*args, **kwargs)
        ds.add_signals(udf, parallel=parallel).save(target_name)

    def query(  # noqa: PLR0912
        self,
        query_script: str,
        envs: Optional[Mapping[str, str]] = None,
        python_executable: Optional[str] = None,
        save: bool = False,
        preview_limit: Optional[int] = 10,
        preview_offset: int = 0,
        preview_columns: Optional[list[str]] = None,
    ) -> QueryResult:
        """
        Method to run custom user Python script to run a query and, as result,
        creates new dataset from the results of a query.
        Returns tuple of result dataset and script output.

        Constraints on query script:
            1. dvcx.query.DatasetQuery should be used in order to create query
            for a dataset
            2. There should not be any .save() call on DatasetQuery since the idea
            is to create only one dataset as the outcome of the script
            3. Last statement must be an instance of DatasetQuery

        If save is set to True, we are creating new dataset with results
        from dataset query. If it's set to False, we will just print results
        without saving anything

        Example of query script:
            from dvcx.query import DatasetQuery, C
            DatasetQuery('s3://ldb-public/remote/datasets/mnist-tiny/').filter(
                C.size > 1000
            )
        """
        if envs is None:
            envs = os.environ

        try:
            query_script_compiled = self.compile_query_script(query_script, save=save)
        except Exception as exc:
            raise QueryScriptCompileError(
                f"Query script failed to compile, reason: {exc}"
            ) from exc

        if not python_executable:
            python_executable = sys.executable

        envs = dict(envs)
        envs.update(
            {
                "DVCX_QUERY_PREVIEW_ARGS": json.dumps(
                    {
                        "limit": preview_limit,
                        "offset": preview_offset,
                        "columns": preview_columns,
                    }
                )
            }
        )
        result = subprocess.run(
            [python_executable, "-c", query_script_compiled],  # noqa: S603
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # merging stderr to stdout
            env=envs,
            check=False,
        )

        script_output = ""  # stdout + stderr from user script itself

        # finding returning dataset name and version from script
        dataset_name = None
        dataset_version = None
        records = None
        if result.stdout:
            for line in result.stdout.decode("utf-8").splitlines():
                if len(line.split(PYTHON_SCRIPT_WRAPPER_CODE)) == 4:
                    dataset_name = line.split(PYTHON_SCRIPT_WRAPPER_CODE)[1]
                    dataset_version = int(line.split(PYTHON_SCRIPT_WRAPPER_CODE)[2])
                elif (
                    not records
                    and line.startswith("__ds_records__")
                    and line.endswith("__ds_records__")
                ):
                    _, record, _ = line.split("__ds_records__", 2)
                    records = json.loads(record.strip())
                else:
                    # collecting script output as well to save it to the database
                    # later on for debugging
                    script_output += line + "\n"

        if result.returncode:
            if result.returncode == QUERY_SCRIPT_CANCELED_EXIT_CODE:
                raise QueryScriptCancelError(
                    "Query script was canceled by user",
                    return_code=result.returncode,
                    output=script_output,
                )
            if result.returncode == QUERY_SCRIPT_INVALID_LAST_STATEMENT_EXIT_CODE:
                raise QueryScriptRunError(
                    "Last line in a script was not an instance of DatasetQuery",
                    return_code=result.returncode,
                    output=script_output,
                )
            raise QueryScriptRunError(
                f"Query script exited with error code {result.returncode}",
                return_code=result.returncode,
                output=script_output,
            )

        if not save:
            return QueryResult(
                dataset=None, version=None, output=script_output, preview=records
            )

        # finding returning dataset
        returned_dataset = None
        returned_dataset_version = None
        if dataset_name and dataset_version:
            try:
                returned_dataset = self.get_dataset(dataset_name)
                returned_dataset_version = returned_dataset.get_version(dataset_version)
            except DatasetNotFoundError:
                pass

        if not returned_dataset or not returned_dataset_version:
            raise QueryScriptDatasetNotFound(
                "No dataset found after running Query script",
                output=script_output,
            )

        returned_dataset = self.update_dataset(
            returned_dataset,
            script_output=script_output,
            query_script=query_script,
        )

        return QueryResult(
            dataset=returned_dataset,
            version=dataset_version,
            output=script_output,
            preview=records,
        )

    def cp(
        self,
        sources: list[str],
        output: str,
        force: bool = False,
        update: bool = False,
        recursive: bool = False,
        edvcx_file: Optional[str] = None,
        edvcx_only: bool = False,
        no_edvcx_file: bool = False,
        no_glob: bool = False,
        ttl: int = TTL_INT,
        *,
        client_config=None,
    ) -> list[dict[str, Any]]:
        """
        This function copies files from cloud sources to local destination directory
        If cloud source is not indexed, or has expired index, it runs indexing
        It also creates .edvcx file by default, if not specified differently
        """
        client_config = client_config or self.client_config
        node_groups = self.enlist_sources_grouped(
            sources,
            ttl,
            update,
            no_glob,
            client_config=client_config,
        )

        always_copy_dir_contents, copy_to_filename = prepare_output_for_cp(
            node_groups, output, force, edvcx_only, no_edvcx_file
        )
        dataset_file = check_output_dataset_file(
            output, force, edvcx_file, no_edvcx_file
        )

        total_size, total_files = collect_nodes_for_cp(node_groups, recursive)

        if total_files == 0:
            # Nothing selected to cp
            return []

        desc_max_len = max(len(output) + 16, 19)
        bar_format = (
            "{desc:<"
            f"{desc_max_len}"
            "}{percentage:3.0f}%|{bar}| {n_fmt:>5}/{total_fmt:<5} "
            "[{elapsed}<{remaining}, {rate_fmt:>8}]"
        )

        if not edvcx_only:
            with get_download_bar(bar_format, total_size) as pbar:
                for node_group in node_groups:
                    node_group.download(recursive=recursive, pbar=pbar)

        instantiate_node_groups(
            node_groups,
            output,
            bar_format,
            total_files,
            force,
            recursive,
            edvcx_only,
            always_copy_dir_contents,
            copy_to_filename,
        )
        if no_edvcx_file:
            return []

        metafile_data = compute_metafile_data(node_groups)
        if metafile_data:
            # Don't write the metafile if nothing was copied
            print(f"Creating '{dataset_file}'")
            with open(dataset_file, "w", encoding="utf-8") as fd:
                yaml.dump(metafile_data, fd, sort_keys=False)

        return metafile_data

    def du(
        self,
        sources,
        depth=0,
        ttl=TTL_INT,
        update=False,
        *,
        client_config=None,
    ) -> Iterable[tuple[str, float]]:
        sources = self.enlist_sources(
            sources,
            ttl,
            update,
            client_config=client_config or self.client_config,
        )

        def du_dirs(src, node, subdepth):
            if subdepth > 0:
                subdirs = src.listing.warehouse.get_nodes_by_parent_path(
                    node.path, type="dir"
                )
                for sd in subdirs:
                    yield from du_dirs(src, sd, subdepth - 1)
            yield (
                src.get_node_full_path(node),
                src.listing.du(node)[0],
            )

        for src in sources:
            yield from du_dirs(src, src.node, depth)

    def find(
        self,
        sources,
        ttl=TTL_INT,
        update=False,
        names=None,
        inames=None,
        paths=None,
        ipaths=None,
        size=None,
        typ=None,
        columns=None,
        *,
        client_config=None,
    ) -> Iterator[str]:
        sources = self.enlist_sources(
            sources,
            ttl,
            update,
            client_config=client_config or self.client_config,
        )
        if not columns:
            columns = ["path"]
        field_set = set()
        for column in columns:
            if column == "du":
                field_set.add("dir_type")
                field_set.add("size")
                field_set.add("parent")
                field_set.add("name")
            elif column == "name":
                field_set.add("name")
            elif column == "owner":
                field_set.add("owner_name")
            elif column == "path":
                field_set.add("dir_type")
                field_set.add("parent")
                field_set.add("name")
            elif column == "size":
                field_set.add("size")
            elif column == "type":
                field_set.add("dir_type")
        fields = list(field_set)
        field_lookup = {f: i for i, f in enumerate(fields)}
        for src in sources:
            results = src.listing.find(
                src.node, fields, names, inames, paths, ipaths, size, typ
            )
            for row in results:
                yield "\t".join(
                    find_column_to_str(row, field_lookup, src, column)
                    for column in columns
                )

    def index(
        self,
        sources,
        ttl=TTL_INT,
        update=False,
        *,
        client_config=None,
        index_processors: Optional[Union[list[IndexingFormat], IndexingFormat]] = None,
    ) -> None:
        root_sources = [
            src for src in sources if Client.get_implementation(src).is_root_url(src)
        ]
        non_root_sources = [
            src
            for src in sources
            if not Client.get_implementation(src).is_root_url(src)
        ]

        client_config = client_config or self.client_config

        # for root sources (e.g s3://) we are just getting all buckets and
        # saving them as storages, without further indexing in each bucket
        for source in root_sources:
            for bucket in Client.get_implementation(source).ls_buckets(**client_config):
                client = self.get_client(bucket.uri, **client_config)
                print(f"Registering storage {client.uri}")
                self.metastore.create_storage_if_not_registered(client.uri)

        if index_processors and not isinstance(index_processors, list):
            processors = [index_processors]
        else:
            processors = index_processors  # type: ignore
        self.enlist_sources(
            non_root_sources,
            ttl,
            update,
            client_config=client_config,
            index_processors=processors,
            only_index=True,
        )

    def find_stale_storages(self) -> None:
        self.metastore.find_stale_storages()
