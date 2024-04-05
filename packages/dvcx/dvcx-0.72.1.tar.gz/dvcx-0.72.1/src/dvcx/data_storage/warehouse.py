import json
import logging
import posixpath
from abc import ABC, abstractmethod
from collections.abc import Generator, Iterable, Iterator, Sequence
from random import getrandbits
from typing import TYPE_CHECKING, Any, Optional, Union
from urllib.parse import urlparse

import attrs
import sqlalchemy as sa
from sqlalchemy import Table, and_, case, select
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import true

from dvcx.data_storage.schema import DATASET_CORE_COLUMN_NAMES, SignalsTable
from dvcx.data_storage.schema import Node as NodeTable
from dvcx.data_storage.serializer import Serializable
from dvcx.dataset import DatasetRecord, DatasetRow
from dvcx.node import DirTypeGroup, Entry, Node, NodeWithPath, get_path
from dvcx.sql.types import Int, SQLType
from dvcx.storage import StorageURI
from dvcx.utils import GLOB_CHARS, sql_escape_like

if TYPE_CHECKING:
    from sqlalchemy.sql.elements import ColumnElement
    from sqlalchemy.types import TypeEngine

    from dvcx.data_storage import AbstractIDGenerator, schema
    from dvcx.data_storage.db_engine import DatabaseEngine

try:
    import numpy as np

    numpy_imported = True
except ImportError:
    numpy_imported = False


logger = logging.getLogger("dvcx")

RANDOM_BITS = 63  # size of the random integer field

SELECT_BATCH_SIZE = 100_000  # number of rows to fetch at a time

# special string to wrap around dataset name in a user query script stdout, which
# is run in a Python subprocess, so that we can find it later on after script is
# done since there is no other way to return results from it
PYTHON_SCRIPT_WRAPPER_CODE = "__ds__"


class AbstractWarehouse(ABC, Serializable):
    """
    Abstract Warehouse class, to be implemented by any Database Adapters
    for a specific database system. This manages the storing, searching, and
    retrieval of datasets data, and has shared logic for all database
    systems currently in use.
    """

    #
    # Constants, Initialization, and Tables
    #

    BUCKET_TABLE_NAME_PREFIX = "src_"
    DATASET_TABLE_PREFIX = "ds_"
    SIGNALS_TABLE_PREFIX = "sg_"

    id_generator: "AbstractIDGenerator"
    schema: "schema.Schema"
    db: "DatabaseEngine"

    def __init__(
        self,
        id_generator: "AbstractIDGenerator",
        uri: StorageURI = StorageURI(""),
        partial_id: Optional[int] = None,
    ):
        self.id_generator = id_generator
        self.uri = uri
        self.partial_id: Optional[int] = partial_id
        self._nodes: Optional["schema.Node"] = None
        self.node_fields = [c.name for c in self.schema.node_cls.default_columns()]

    def cleanup_for_tests(self):  # noqa: B027
        """Cleanup for tests."""

    def convert_type(self, val: Any, col_type: SQLType) -> Any:  # noqa: PLR0911
        """
        Tries to convert value to specific type if needed and if compatible,
        otherwise throws an ValueError.
        If value is a list or some other iterable, it tries to convert sub elements
        as well
        """
        if numpy_imported and isinstance(val, (np.ndarray, np.generic)):
            val = val.tolist()

        col_python_type = self.python_type(col_type)
        value_type = type(val)

        exc = None
        try:
            if col_python_type == list and value_type in (list, tuple, set):
                if len(val) == 0:
                    return []
                item_pyton_type = self.python_type(col_type.item_type)
                if item_pyton_type != list:
                    if isinstance(val[0], item_pyton_type):
                        return val
                    if item_pyton_type == float and isinstance(val[0], int):
                        return [float(i) for i in val]
                return [self.convert_type(i, col_type.item_type) for i in val]
            # special use case with JSON type as we save it as string
            if col_python_type == dict:
                if value_type == str:
                    return val
                elif value_type in (dict, list):
                    return json.dumps(val)
                else:
                    raise ValueError(
                        f"Cannot convert value {val!r} with type"
                        f"{value_type} to JSON"
                    )

            if isinstance(val, col_python_type):
                return val
            if col_python_type == float and isinstance(val, int):
                return float(val)
        except Exception as e:
            exc = e
        raise ValueError(
            f"Value {val!r} with type {value_type} incompatible for "
            f"column type {type(col_type).__name__}"
        ) from exc

    @abstractmethod
    def clone(
        self, uri: StorageURI = StorageURI(""), partial_id: Optional[int] = None
    ) -> "AbstractWarehouse":
        """Clones Warehouse implementation for some Storage input"""

    def close(self) -> None:
        """Closes any active database connections."""
        self.db.close()

    @abstractmethod
    def init_db(self, uri: StorageURI, partial_id: int) -> None:
        """Initializes database tables for warehouse"""

    #
    # Query Tables
    #

    @property
    def nodes(self):
        assert (
            self.current_bucket_table_name
        ), "Nodes can only be used if uri/current_bucket_table_name is set"
        if self._nodes is None:
            self._nodes = self.schema.node_cls(
                self.current_bucket_table_name, self.uri, self.db.metadata
            )
        return self._nodes

    def nodes_table(self, source_uri: str, partial_id: Optional[int] = None):
        if partial_id is None:
            raise ValueError("missing partial_id")
        table_name = self.bucket_table_name(source_uri, partial_id)
        return self.schema.node_cls(table_name, source_uri, self.db.metadata)

    def dataset_rows(self, dataset: DatasetRecord, version: Optional[int] = None):
        version = version or dataset.latest_version

        table_name = self.dataset_table_name(dataset.name, version)
        return self.schema.dataset_row_cls(
            table_name,
            self.db.engine,
            self.db.metadata,
            dataset.get_custom_column_types(version),
        )

    @property
    def dataset_row_cls(self):
        return self.schema.dataset_row_cls

    #
    # Query Execution
    #

    def dataset_select_paginated(
        self,
        query,
        limit: Optional[int] = None,
        order_by: Sequence[str] = (),
        page_size: int = SELECT_BATCH_SIZE,
    ) -> Generator[DatasetRow, None, None]:
        """
        This is equivalent to `db.execute`, but for selecting rows in batches
        """
        cols = query.selected_columns
        cols_names = [c.name for c in cols]

        if not order_by:
            ordering = [cols.source, cols.parent, cols.name, cols.version, cols.etag]
        else:
            ordering = order_by  # type: ignore

        # reset query order by and apply new order by id
        paginated_query = query.order_by(None).order_by(*ordering).limit(page_size)

        offset = 0
        num_yielded = 0
        while True:
            if limit:
                limit -= num_yielded
                if limit == 0:
                    break
                if limit < page_size:
                    paginated_query = paginated_query.limit(None).limit(limit)

            results = self.db.execute(paginated_query.offset(offset))

            processed = False
            for row in results:
                processed = True
                yield DatasetRow.from_result_row(cols_names, row)
                num_yielded += 1

            if not processed:
                break  # no more results
            offset += page_size

    #
    # Table Name Internal Functions
    #

    @staticmethod
    def uri_to_storage_info(uri: str) -> tuple[str, str]:
        parsed = urlparse(uri)
        name = parsed.path if parsed.scheme == "file" else parsed.netloc
        return parsed.scheme, name

    def bucket_table_name(self, uri: str, version: int) -> str:
        scheme, name = self.uri_to_storage_info(uri)
        return f"{self.BUCKET_TABLE_NAME_PREFIX}{scheme}_{name}_{version}"

    def signals_table_name(self, uri: str, version: int = 0) -> str:
        parsed = urlparse(uri)
        return f"{self.SIGNALS_TABLE_PREFIX}{parsed.scheme}_{parsed.netloc}_{version}"

    def dataset_table_name(self, dataset_name: str, version: int) -> str:
        return f"{self.DATASET_TABLE_PREFIX}{dataset_name}_{version}"

    @property
    def current_bucket_table_name(self) -> Optional[str]:
        if not self.uri:
            return None

        # We want to make sure that partial_id is reused when calling
        # warehouse.clone(). It should only be calculated once per
        # listing, so we don't call get_valid_partial_id here
        if self.partial_id is None:
            raise ValueError("missing partial_id")

        return self.bucket_table_name(self.uri, self.partial_id)

    #
    # Datasets
    #

    @abstractmethod
    def create_dataset_rows_table(
        self,
        name: str,
        custom_columns: Sequence["sa.Column"] = (),
        if_not_exists: bool = True,
    ) -> Table:
        """Creates a dataset rows table for the given dataset name and columns"""

    def drop_dataset_rows_table(
        self,
        dataset: DatasetRecord,
        version: int,
        if_exists: bool = True,
    ) -> None:
        """Drops a dataset rows table for the given dataset name."""
        table_name = self.dataset_table_name(dataset.name, version)
        table = Table(table_name, self.db.metadata)
        self.db.drop_table(table, if_exists=if_exists)

    @abstractmethod
    def merge_dataset_rows(
        self,
        src: "DatasetRecord",
        dst: "DatasetRecord",
        src_version: int,
        dst_version: int,
    ) -> None:
        """
        Merges source dataset rows and current latest destination dataset rows
        into a new rows table created for new destination dataset version.
        Note that table for new destination version must be created upfront.
        Merge results should not contain duplicates.
        """

    @abstractmethod
    def dataset_rows_select(self, select_query: sa.sql.selectable.Select, **kwargs):
        """
        Method for fetching dataset rows from database. This is abstract since
        in some DBs we need to use special settings
        """

    @abstractmethod
    def get_dataset_sources(
        self, dataset: DatasetRecord, version: int
    ) -> list[StorageURI]: ...

    def get_dataset_rows(
        self,
        dataset: DatasetRecord,
        version: int,
        offset: Optional[int] = 0,
        limit: Optional[int] = 20,
        custom_columns=False,
        source: Optional[str] = None,
    ) -> Iterator[DatasetRow]:
        """Gets dataset rows."""
        # if custom_columns are to be returned, we are setting columns to None to
        # retrieve all columns from a table (default ones and custom)
        columns = list(DATASET_CORE_COLUMN_NAMES) if not custom_columns else None
        dr = self.dataset_rows(dataset, version)

        if not columns:
            # fetching all columns if specific columns are not defined
            columns = [c.name for c in dr.c]

        select_columns = [dr.c[c] for c in columns]
        column_index_mapping = {c: i for i, c in enumerate(columns)}

        query = dr.select(*select_columns)
        if source:
            query = query.where(dr.c.source == source)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        # ordering by primary key / index
        query = query.order_by("id")

        def map_row_to_dict(row):
            return {c: row[i] for c, i in column_index_mapping.items()}

        for row in self.dataset_rows_select(query):
            yield DatasetRow.from_dict(map_row_to_dict(row))

    def nodes_dataset_query(
        self,
        column_names: Optional[Iterable[str]] = None,
        path: Optional[str] = None,
        recursive: Optional[bool] = False,
        uri: Optional[str] = None,
    ) -> "sa.Select":
        """
        Provides a query object representing the given `uri` as a dataset.

        If `uri` is not given then `self.uri` is used. The given `column_names`
        will be selected in the order they're given. `path` is a glob which
        will select files in matching directories, or if `recursive=True` is
        set then the entire tree under matching directories will be selected.
        """

        def _is_glob(path: str) -> bool:
            return any(c in path for c in ["*", "?", "[", "]"])

        assert uri == self.uri
        n = self.nodes
        select_query = n.dataset_query(*(column_names or []))
        if path is None:
            return select_query
        if recursive:
            root = False
            if not path or path == "/":
                # root of the bucket, e.g s3://bucket/ -> getting all the nodes
                # in the bucket
                root = True

            if not root and not _is_glob(path):
                # not a root and not a explicit glob, so it's pointing to some directory
                # and we are adding a proper glob syntax for it
                # e.g s3://bucket/dir1 -> s3://bucket/dir1/*
                path = path.rstrip("/") + "/*"

            if not root:
                # not a root, so running glob query
                select_query = select_query.where(self.path_expr(n).op("GLOB")(path))
        else:
            parent = self.get_node_by_path(path.lstrip("/").rstrip("/*"))
            select_query = select_query.where(n.c.parent == parent.path)
        return select_query

    def rename_dataset_table(
        self,
        old_name: str,
        new_name: str,
        old_version: int,
        new_version: int,
    ) -> None:
        old_ds_table_name = self.dataset_table_name(old_name, old_version)
        new_ds_table_name = self.dataset_table_name(new_name, new_version)

        self.db.rename_table(old_ds_table_name, new_ds_table_name)

    def dataset_rows_count(self, dataset: DatasetRecord, version=None) -> int:
        """Returns total number of rows in a dataset"""
        dr = self.dataset_rows(dataset, version)
        query = select(sa.func.count()).select_from(dr.get_table())
        (res,) = self.db.execute(query)
        return res[0]

    def dataset_stats(self, dataset: DatasetRecord, version: int) -> tuple[int, int]:
        """
        Returns tuple with dataset stats: total number of rows and total dataset size.
        """
        dr = self.dataset_rows(dataset, version)
        query = select(sa.func.count(), sa.func.sum(dr.c.size)).select_from(
            dr.get_table()
        )
        (res,) = self.db.execute(query)
        return res[0], res[1]

    #
    # Nodes
    #

    @abstractmethod
    def insert_node(self, entry: Entry) -> None:
        """
        Inserts file or directory node into the database
        """

    @abstractmethod
    def insert_nodes(self, entries: Iterable[Entry]) -> None:
        """Inserts file or directory nodes into the database"""

    def insert_nodes_done(self):  # noqa: B027
        """
        Only needed for certain implementations
        to signal when node inserts are complete.
        """

    @abstractmethod
    def insert_rows(self, table: Table, rows: Iterable[dict[str, Any]]) -> None:
        """Does batch inserts of any kind of rows into table"""

    def insert_rows_done(self, table: Table) -> None:  # noqa: B027
        """
        Only needed for certain implementations
        to signal when rows inserts are complete.
        """

    @abstractmethod
    def insert_dataset_rows(self, df, dataset: DatasetRecord, version: int) -> int:
        """Inserts dataset rows directly into dataset table"""

    @abstractmethod
    def instr(self, source, target) -> "ColumnElement":
        """
        Return SQLAlchemy Boolean determining if a target substring is present in
        source string column
        """

    @abstractmethod
    def get_table(self, name: str) -> sa.Table:
        """
        Returns a SQLAlchemy Table object by name. If table doesn't exist, it should
        create it
        """

    @abstractmethod
    def add_column(self, table: Table, col_name: str, col_type: "TypeEngine") -> None:
        """Adds a column with a name and type to a table"""

    @abstractmethod
    def dataset_table_export_file_names(
        self, dataset: DatasetRecord, version: int
    ) -> list[str]:
        """
        Returns list of file names that will be created when user runs dataset export
        """

    @abstractmethod
    def export_dataset_table(
        self,
        bucket_uri: str,
        dataset: DatasetRecord,
        version: int,
        client_config=None,
    ) -> list[str]:
        """
        Exports dataset table to the cloud, e.g to some s3 bucket
        """

    def python_type(self, col_type: Union["TypeEngine", "SQLType"]) -> Any:
        """Returns python type representation of some Sqlalchemy column type"""
        return col_type.python_type

    def _prepare_node(self, entry: Entry) -> dict[str, Any]:
        assert entry.dir_type is not None
        d = {
            "source": self.uri,
            "random": getrandbits(RANDOM_BITS),
            "parent_id": None,
            **attrs.asdict(entry),
        }
        return {f: d.get(f) for f in self.node_fields[1:]}

    def add_node_type_where(
        self,
        query,
        type: Optional[str],
        include_subobjects: bool = True,
    ):
        if type is None:
            return query

        file_group: Sequence[int]
        if type in {"f", "file", "files"}:
            if include_subobjects:
                file_group = DirTypeGroup.SUBOBJ_FILE
            else:
                file_group = DirTypeGroup.FILE
        elif type in {"d", "dir", "directory", "directories"}:
            if include_subobjects:
                file_group = DirTypeGroup.SUBOBJ_DIR
            else:
                file_group = DirTypeGroup.DIR
        else:
            raise ValueError(f"invalid file type: {type!r}")

        c = query.selected_columns
        q = query.where(c.dir_type.in_(file_group))
        if not include_subobjects:
            q = q.where(c.vtype == "")
        return q

    def get_nodes(self, query) -> Iterator[Node]:
        """
        This gets nodes based on the provided query, and should be used sparingly,
        as it will be slow on any OLAP database systems.
        """
        return (Node(*row) for row in self.db.execute(query))

    def get_nodes_by_parent_path(
        self,
        parent_path: str,
        type: Optional[str] = None,
    ) -> Iterator[Node]:
        """Gets nodes from database by parent path, with optional filtering"""
        n = self.nodes
        where_cond = (n.c.parent == parent_path) & (n.c.is_latest == true())
        if parent_path == "":
            # Exclude the root dir
            where_cond = where_cond & (n.c.name != "")
        query = n.select(*n.default_columns()).where(where_cond)
        query = self.add_node_type_where(query, type)
        query = query.order_by(n.c.source, n.c.parent, n.c.name, n.c.version, n.c.etag)
        return self.get_nodes(query)

    def _get_nodes_by_glob_path_pattern(
        self, path_list: list[str], glob_name: str
    ) -> Iterator[Node]:
        """Finds all Nodes that correspond to GLOB like path pattern."""
        n = self.nodes
        path_glob = "/".join(path_list + [glob_name])
        dirpath = path_glob[: -len(glob_name)]
        relpath = func.substr(self.path_expr(n), len(dirpath) + 1)

        return self.get_nodes(
            n.select(*n.default_columns())
            .where(
                (self.path_expr(n).op("GLOB")(path_glob))
                & (n.c.is_latest == true())
                & ~self.instr(relpath, "/")
                & (self.path_expr(n) != dirpath)
            )
            .order_by(n.c.source, n.c.parent, n.c.name, n.c.version, n.c.etag)
        )

    def _get_node_by_path_list(self, path_list: list[str], name: str) -> Node:
        """
        Gets node that correspond some path list, e.g ["data-lakes", "dogs-and-cats"]
        """
        parent = "/".join(path_list)
        n = self.nodes
        row = next(
            self.db.execute(
                n.select(*n.default_columns())
                .where(
                    (n.c.parent == parent)
                    & (n.c.name == name)
                    & (n.c.is_latest == true())
                )
                .order_by(n.c.source, n.c.parent, n.c.name, n.c.version, n.c.etag)
            ),
            None,
        )
        if not row:
            path = f"{parent}/{name}"
            raise FileNotFoundError(f"Unable to resolve path {path!r}")
        return Node(*row)

    def _populate_nodes_by_path(self, path_list: list[str]) -> list[Node]:
        """
        Puts all nodes found by path_list into the res input variable.
        Note that path can have GLOB like pattern matching which means that
        res can have multiple nodes as result.
        If there is no GLOB pattern, res should have one node as result that
        match exact path by path_list
        """
        if not path_list:
            return [self._get_node_by_path_list([], "")]
        matched_paths: list[list[str]] = [[]]
        for curr_name in path_list[:-1]:
            if set(curr_name).intersection(GLOB_CHARS):
                new_paths = []
                for path in matched_paths:
                    nodes = self._get_nodes_by_glob_path_pattern(path, curr_name)
                    for node in nodes:
                        if node.is_container:
                            new_paths.append(path + [node.name or ""])
                matched_paths = new_paths
            else:
                for path in matched_paths:
                    path.append(curr_name)
        curr_name = path_list[-1]
        if set(curr_name).intersection(GLOB_CHARS):
            result: list[Node] = []
            for path in matched_paths:
                nodes = self._get_nodes_by_glob_path_pattern(path, curr_name)
                result.extend(nodes)
        else:
            result = [
                self._get_node_by_path_list(path, curr_name) for path in matched_paths
            ]
        return result

    def get_node_by_path(self, path: str) -> Node:
        """Gets node that corresponds to some path"""
        n = self.nodes
        query = n.select(*n.default_columns()).where(
            (self.path_expr(n) == path.strip("/")) & (n.c.is_latest == true())
        )
        if path.endswith("/"):
            query = self.add_node_type_where(query, "dir")

        query = query.order_by(n.c.source, n.c.parent, n.c.name, n.c.version, n.c.etag)
        row = next(self.db.execute(query), None)
        if not row:
            raise FileNotFoundError(f"Unable to resolve path {path}")
        return Node(*row)

    def expand_path(self, path: str) -> list[Node]:
        """Simulates Unix-like shell expansion"""
        clean_path = path.strip("/")
        path_list = clean_path.split("/") if clean_path != "" else []
        res = self._populate_nodes_by_path(path_list)
        if path.endswith("/"):
            res = [node for node in res if node.dir_type in DirTypeGroup.SUBOBJ_DIR]
        return res

    def select_node_fields_by_parent_path(
        self,
        parent_path: str,
        fields: Iterable[str],
    ) -> Iterator[tuple[Any, ...]]:
        """
        Gets latest-version file nodes from the provided parent path
        """
        n = self.nodes
        where_cond = (n.c.parent == parent_path) & (n.c.is_latest == true())
        if parent_path == "":
            # Exclude the root dir
            where_cond = where_cond & (n.c.name != "")
        return self.db.execute(
            n.select(*(getattr(n.c, f) for f in fields))
            .where(where_cond)
            .order_by(n.c.source, n.c.parent, n.c.name, n.c.version, n.c.etag)
        )

    def select_node_fields_by_parent_path_tar(
        self, parent_path: str, fields: Iterable[str]
    ) -> Iterator[tuple[Any, ...]]:
        """
        Gets latest-version file nodes from the provided parent path
        """
        n = self.nodes
        dirpath = f"{parent_path}/"
        relpath = func.substr(self.path_expr(n), len(dirpath) + 1)

        def field_to_expr(f):
            if f == "name":
                return relpath
            return getattr(n.c, f)

        q = (
            select(*(field_to_expr(f) for f in fields))
            .where(
                self.path_expr(n).like(f"{sql_escape_like(dirpath)}%"),
                ~self.instr(relpath, "/"),
                n.c.is_latest == true(),
            )
            .order_by(n.c.source, n.c.parent, n.c.name, n.c.version, n.c.etag)
        )
        return self.db.execute(q)

    def size(
        self, node: Union[Node, dict[str, Any]], count_files: bool = False
    ) -> tuple[int, int]:
        """
        Calculates size of some node (and subtree below node).
        Returns size in bytes as int and total files as int
        """
        if isinstance(node, dict):
            is_dir = node.get("is_dir", node["dir_type"] in DirTypeGroup.SUBOBJ_DIR)
            node_size = node["size"]
            path = get_path(node["parent"], node["name"])
        else:
            is_dir = node.is_container
            node_size = node.size
            path = node.path
        if not is_dir:
            # Return node size if this is not a directory
            return node_size, 1

        sub_glob = posixpath.join(path, "*")
        n = self.nodes
        selections = [
            func.sum(n.c.size),
        ]
        if count_files:
            selections.append(
                func.sum(n.c.dir_type.in_(DirTypeGroup.FILE)),
            )
        results = next(
            self.db.execute(
                n.select(*selections).where(
                    (self.path_expr(n).op("GLOB")(sub_glob)) & (n.c.is_latest == true())
                )
            ),
            (0, 0),
        )
        if count_files:
            return results[0] or 0, results[1] or 0
        else:
            return results[0] or 0, 0

    def path_expr(self, t):
        return case((t.c.parent == "", t.c.name), else_=t.c.parent + "/" + t.c.name)

    def _find_query(
        self,
        node: Node,
        query,
        type: Optional[str] = None,
        conds=None,
        order_by: Optional[Union[str, list[str]]] = None,
    ) -> Any:
        if not conds:
            conds = []

        n = self.nodes
        path = self.path_expr(n)

        if node.path:
            sub_glob = posixpath.join(node.path, "*")
            conds.append(path.op("GLOB")(sub_glob))
        else:
            conds.append(path != "")

        query = query.where(
            and_(
                *conds,
                n.c.is_latest == true(),
            )
        )
        if type is not None:
            query = self.add_node_type_where(query, type)
        if order_by is not None:
            if isinstance(order_by, str):
                order_by = [order_by]
            query = query.order_by(*(getattr(n.c, col) for col in order_by))
        return query

    def get_subtree_files(
        self,
        node: Node,
        sort: Union[list[str], str, None] = None,
        include_subobjects: bool = True,
    ) -> Iterator[NodeWithPath]:
        """
        Returns all file nodes that are "below" some node.
        Nodes can be sorted as well.
        """
        n = self.nodes
        query = self._find_query(node, n.select(n.default_columns()))
        query = self.add_node_type_where(query, "f", include_subobjects)

        if sort is not None:
            if not isinstance(sort, list):
                sort = [sort]
            query = query.order_by(*(sa.text(s) for s in sort))  # type: ignore [attr-defined]

        prefix_len = len(node.path)

        def make_node_with_path(row):
            sub_node = Node(*row)
            return NodeWithPath(
                sub_node, sub_node.path[prefix_len:].lstrip("/").split("/")
            )

        return map(make_node_with_path, self.db.execute(query))

    def find(
        self,
        node: Node,
        fields: Iterable[str],
        type=None,
        conds=None,
        order_by=None,
    ) -> Iterator[tuple[Any, ...]]:
        """
        Finds nodes that match certain criteria and only looks for latest nodes
        under the passed node.
        """
        n = self.nodes
        query = self._find_query(
            node,
            n.select(*(getattr(n.c, f) for f in fields)),
            type,
            conds,
            order_by=order_by,
        )
        return self.db.execute(query)

    def update_type(self, node_id: int, dir_type: int) -> None:
        """Updates type of specific node in database"""
        n = self.nodes
        self.db.execute(
            self.nodes.update().where(n.c.id == node_id).values(dir_type=dir_type)  # type: ignore [attr-defined]
        )

    def update_node(self, node_id: int, values: dict[str, Any]) -> None:
        """Update entry of a specific node in the database."""
        n = self.nodes
        self.db.execute(self.nodes.update().values(**values).where(n.c.id == node_id))

    def storage_stats(
        self, uri: StorageURI, partial_id: Optional[int]
    ) -> tuple[int, int]:
        """
        Returns tuple with storage stats: total number of rows and total dataset size.
        """
        n = self.nodes_table(uri, partial_id)
        query = select(sa.func.count(), sa.func.sum(n.c.size)).select_from(
            n.get_table()
        )
        (res,) = self.db.execute(query)
        return res[0], res[1]

    def return_ds_hook(self, name: str, version: int) -> None:
        """
        Hook to be run when a return ds is ready to be saved in a
        DatasetQuery script.
        """
        print(
            f"{PYTHON_SCRIPT_WRAPPER_CODE}{name}{PYTHON_SCRIPT_WRAPPER_CODE}"
            f"{version}{PYTHON_SCRIPT_WRAPPER_CODE}"
        )

    def create_udf_table(
        self,
        name: str,
        custom_columns: Sequence["sa.Column"] = (),
    ) -> "sa.Table":
        """
        Create a temporary table for storing custom signals generated by a UDF.
        SQLite TEMPORARY tables cannot be directly used as they are process-specific,
        and UDFs are run in other processes when run in parallel.
        """
        tbl = sa.Table(
            name,
            sa.MetaData(),
            sa.Column("id", Int, primary_key=True),
            *custom_columns,
        )
        self.db.create_table(tbl, if_not_exists=True)
        return tbl

    def cleanup_temp_tables(self, names: Iterable[str]) -> None:
        """
        Drop tables created temporarily when processing datasets.

        This should be implemented even if temporary tables are used to
        ensure that they are cleaned up as soon as they are no longer
        needed. When running the same `DatasetQuery` multiple times we
        may use the same temporary table names.
        """
        for name in names:
            self.db.drop_table(Table(name, self.db.metadata), if_exists=True)

    #
    # Signals
    #

    @abstractmethod
    def create_signals_table(self) -> SignalsTable:
        """
        Create an empty signals table for storing signals entries.
        Signals columns will be added gradually as they are encountered during
        data traversal
        """

    @abstractmethod
    def extend_index_with_signals(self, index: NodeTable, signals: SignalsTable):
        """Extend a nodes table with a signals table."""

    def subtract_query(
        self,
        source_query: sa.sql.selectable.Select,
        target_query: sa.sql.selectable.Select,
    ) -> sa.sql.selectable.Select:
        sq = source_query.alias("source_query")
        tq = target_query.alias("target_query")

        source_target_join = sa.join(
            sq,
            tq,
            (sq.c.source == tq.c.source)
            & (sq.c.parent == tq.c.parent)
            & (sq.c.name == tq.c.name),
            isouter=True,
        )

        return (
            select(sq.c)
            .select_from(source_target_join)
            .where((tq.c.name == None) | (tq.c.name == ""))  # noqa: E711
        )

    def changed_query(
        self,
        source_query: sa.sql.selectable.Select,
        target_query: sa.sql.selectable.Select,
    ) -> sa.sql.selectable.Select:
        sq = source_query.alias("source_query")
        tq = target_query.alias("target_query")

        source_target_join = sa.join(
            sq,
            tq,
            (sq.c.source == tq.c.source)
            & (sq.c.parent == tq.c.parent)
            & (sq.c.name == tq.c.name),
        )

        return (
            select(sq.c)
            .select_from(source_target_join)
            .where(
                (sq.c.last_modified > tq.c.last_modified)
                & (sq.c.is_latest == true())
                & (tq.c.is_latest == true())
            )
        )
