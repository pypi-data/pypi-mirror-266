import contextlib
import datetime
import json
import logging
import os
import random
import re
import string
import subprocess
import sys
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Sequence
from copy import copy
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    Protocol,
    TypeVar,
    Union,
)

import attrs
import sqlalchemy
from attrs import frozen
from dill import dumps
from sqlalchemy.sql import func as f
from sqlalchemy.sql.elements import ColumnClause, ColumnElement
from sqlalchemy.sql.expression import label
from sqlalchemy.sql.visitors import TraversibleType

from dvcx.asyn import ASYNC_WORKERS, AsyncMapper, OrderedMapper
from dvcx.catalog import (
    QUERY_SCRIPT_CANCELED_EXIT_CODE,
    QUERY_SCRIPT_INVALID_LAST_STATEMENT_EXIT_CODE,
    get_catalog,
)
from dvcx.data_storage.schema import (
    DATASET_CORE_COLUMN_NAMES,
    PARTITION_COLUMN_ID,
    partition_col_names,
    partition_columns,
)
from dvcx.dataset import DatasetRow
from dvcx.dataset import Status as DatasetStatus
from dvcx.error import DatasetNotFoundError, QueryScriptCancelError
from dvcx.sql.types import SQLType
from dvcx.storage import StorageURI
from dvcx.utils import chunk, determine_processes

from .schema import C, UDFParamSpec, normalize_param
from .udf import UDFBase, UDFClassWrapper, UDFFactory, UDFType

if TYPE_CHECKING:
    from sqlalchemy.sql.schema import Table
    from sqlalchemy.sql.selectable import GenerativeSelect, SelectBase
    from typing_extensions import Concatenate, ParamSpec, Self

    from dvcx.catalog import Catalog
    from dvcx.data_storage import AbstractWarehouse
    from dvcx.dataset import DatasetRecord

    from .udf import UDFResult

    P = ParamSpec("P")


INSERT_BATCH_SIZE = 10000

PartitionByType = Union[ColumnElement, Sequence[ColumnElement]]
JoinPredicateType = Union[str, ColumnClause, ColumnElement]
S = TypeVar("S", bound="SelectBase")
# dependency can be either dataset_name + dataset_version tuple or just storage uri
# depending what type of dependency we are adding
DatasetDependencyType = Union[tuple[str, int], StorageURI]

logger = logging.getLogger("dvcx")


T = TypeVar("T", bound="DatasetQuery")


def detach(
    method: "Callable[Concatenate[T, P], T]",
) -> "Callable[Concatenate[T, P], T]":
    """
    Decorator that needs to be put on a method that modifies existing DatasetQuery
    which was 100% representing one particular dataset and had name and version of
    that dataset set, and which returns new instance of it.
    This kind of DatasetQuery, which represent one whole dataset, we return from
    .save() method.
    Example of modifying method is .filter() as that one filters out part
    of a dataset which means DatasetQuery no longer 100% represents it (in this case
    it can represents only a part of it)
    """

    @wraps(method)
    def _inner(self: T, *args: "P.args", **kwargs: "P.kwargs") -> T:
        cloned = method(self, *args, **kwargs)
        cloned.name = None
        cloned.version = None
        return cloned

    return _inner


class QueryGeneratorFunc(Protocol):
    def __call__(self, *columns: ColumnElement) -> "SelectBase": ...


@frozen
class QueryGenerator:
    func: QueryGeneratorFunc
    columns: tuple[ColumnElement, ...]

    def exclude(self, column_names) -> "SelectBase":
        return self.func(*(c for c in self.columns if c.name not in column_names))

    def select(self, column_names=None) -> "SelectBase":
        if column_names is None:
            return self.func(*self.columns)
        return self.func(*(c for c in self.columns if c.name in column_names))


@frozen
class StepResult:
    query_generator: QueryGenerator
    temp_table_names: tuple[str, ...]
    dependencies: tuple[DatasetDependencyType, ...]


def step_result(
    func: QueryGeneratorFunc,
    columns: Iterable[ColumnElement],
    temp_table_names: Iterable[str] = (),
    dependencies: Iterable[DatasetDependencyType] = (),
) -> "StepResult":
    return StepResult(
        query_generator=QueryGenerator(func=func, columns=tuple(columns)),
        temp_table_names=tuple(temp_table_names),
        dependencies=tuple(dependencies),
    )


class StartingStep(ABC):
    """An initial query processing step, referencing a data source."""

    @abstractmethod
    def apply(self) -> "StepResult": ...


@frozen
class Step(ABC):
    """A query processing step (filtering, mutation, etc.)"""

    @abstractmethod
    def apply(self, query_generator: "QueryGenerator") -> "StepResult":
        """Apply the processing step."""


@frozen
class QueryStep(StartingStep):
    catalog: "Catalog"
    dataset_name: str
    dataset_version: int

    def apply(self):
        """Return the query for the table the query refers to."""

        def q(*columns):
            return sqlalchemy.select(*columns)

        dataset = self.catalog.get_dataset(self.dataset_name)
        table = self.catalog.warehouse.dataset_rows(dataset, self.dataset_version)

        return step_result(
            q, table.c, dependencies=[(self.dataset_name, self.dataset_version)]
        )


@frozen
class IndexingStep(StartingStep):
    path: str
    catalog: "Catalog"
    kwargs: dict[str, Any]
    recursive: Optional[bool] = True

    def apply(self):
        """Return the query for the table the query refers to."""
        # TODO return metastore and warehouse from this index() call and use them below
        self.catalog.index([self.path], **self.kwargs)
        metastore = self.catalog.metastore
        warehouse = self.catalog.warehouse
        uri, path = self.parse_path()

        partial_id = metastore.get_valid_partial_id(uri, path)
        st = warehouse.clone(uri, partial_id)

        def q(*columns):
            col_names = [c.name for c in columns]
            return st.nodes_dataset_query(
                column_names=col_names, path=path, recursive=self.recursive, uri=uri
            )

        dataset_columns = warehouse.dataset_row_cls.calculate_all_columns([st.nodes])
        storage = self.catalog.get_storage(uri)
        return step_result(q, dataset_columns, dependencies=[storage.uri])

    def parse_path(self):
        client_config = self.kwargs.get("client_config") or {}
        client, path = self.catalog.parse_url(self.path, **client_config)
        return client.uri, path


def generator_then_call(generator, func: Callable):
    """
    Yield items from generator then execute a function and yield
    its result.
    """
    yield from generator
    yield func() or []


class DatasetDiffOperation(Step):
    """
    Abstract class for operations that are calculation some kind of diff between
    datasets queries like subtract, changed etc.
    """

    dq: "DatasetQuery"
    catalog: "Catalog"

    def clone(self):
        return self.__class__(self.dq, self.catalog)

    @abstractmethod
    def query(
        self,
        source_query: sqlalchemy.sql.selectable.Select,
        target_query: sqlalchemy.sql.selectable.Select,
    ) -> sqlalchemy.sql.selectable.Select:
        """
        Should return select query that calculates desired diff between dataset queries
        """

    def apply(self, query_generator):
        source_query = query_generator.exclude(("id", "parent_id"))
        target_query = self.dq.apply_steps().select()

        # creating temp table that will hold subtract results
        temp_table_name = "tmp_" + _random_string(6)
        custom_columns = [
            sqlalchemy.Column(col.name, col.type)
            for col in source_query.columns
            if col.name not in DATASET_CORE_COLUMN_NAMES
        ]
        temp_table = self.catalog.warehouse.create_dataset_rows_table(
            temp_table_name,
            custom_columns=custom_columns,
            if_not_exists=False,
        )

        diff_q = self.query(source_query, target_query)

        insert_q = temp_table.insert().from_select(
            source_query.selected_columns, diff_q
        )

        self.catalog.warehouse.db.execute(insert_q)

        def q(*columns):
            return sqlalchemy.select(*columns).select_from(temp_table)

        return step_result(q, temp_table.c, temp_table_names=[temp_table.name])


@frozen
class Subtract(DatasetDiffOperation):
    """
    Calculates rows that are in a source query but are not in target query (diff)
    This can be used to do delta updates (calculate UDF only on newly added rows)
    Example:
        >>> ds = DatasetQuery(name="dogs_cats") # some older dataset with embeddings
        >>> ds_updated = (
                DatasetQuery("gcs://dvcx-datalakes/dogs-and-cats")
                .filter(C.size > 1000) # we can also filter out source query
                .subtract(ds)
                .add_signals(calc_embeddings) # calculae embeddings only on new rows
                .union(ds) # union with old dataset that's missing new rows
                .save("dogs_cats_updated")
            )
    """

    dq: "DatasetQuery"
    catalog: "Catalog"

    def query(self, source_query, target_query) -> sqlalchemy.sql.selectable.Select:
        return self.catalog.warehouse.subtract_query(source_query, target_query)


@frozen
class Changed(DatasetDiffOperation):
    """
    Calculates rows that are changed in a source query compared to target query
    Changed means it has same source + parent + name but different last_modified
    Example:
        >>> ds = DatasetQuery(name="dogs_cats") # some older dataset with embeddings
        >>> ds_updated = (
                DatasetQuery("gcs://dvcx-datalakes/dogs-and-cats")
                .filter(C.size > 1000) # we can also filter out source query
                .changed(ds)
                .add_signals(calc_embeddings) # calculae embeddings only on changed rows
                .union(ds) # union with old dataset that's missing updated rows
                .save("dogs_cats_updated")
            )

    """

    dq: "DatasetQuery"
    catalog: "Catalog"

    def query(self, source_query, target_query) -> sqlalchemy.sql.selectable.Select:
        return self.catalog.warehouse.changed_query(source_query, target_query)


def adjust_outputs(
    warehouse: "AbstractWarehouse", row: dict[str, Any], udf: UDFBase
) -> dict[str, Any]:
    """
    This function does couple of things to prepare row for inserting into db:
    1. Fill default values for columns that have None and add missing ones
    2. Validate values with it's corresponding DB column types and convert types
       if needed and possible
    """
    dialect = warehouse.db.dialect
    for col_name, col_type in udf.output.items():
        row_val = row.get(col_name)

        # fill None or non existing values with defaults
        if col_name not in row or row_val is None:
            row[col_name] = col_type.default_value(dialect)
            continue

        # validate and convert type if needed and possible
        try:
            # check if type is already instantiated or not
            col_type = col_type() if isinstance(col_type, TraversibleType) else col_type
            row[col_name] = warehouse.convert_type(row_val, col_type)
        except ValueError as e:
            logger.exception(
                f"Error while validating/converting type for column "
                f"{col_name} with value {row_val}, original error {e}"
            )
            raise
    return row


def process_udf_outputs(
    warehouse: "AbstractWarehouse",
    udf_table: "Table",
    udf_results: Iterator[Iterable["UDFResult"]],
    udf: UDFBase,
    batch_size=INSERT_BATCH_SIZE,
) -> None:
    rows: list["UDFResult"] = []
    for udf_output in udf_results:
        if not udf_output:
            continue
        for row in udf_output:
            rows.append(adjust_outputs(warehouse, row, udf))
            if len(rows) >= batch_size:
                for row_chunk in chunk(rows, batch_size):
                    warehouse.insert_rows(udf_table, row_chunk)
                rows.clear()

    if rows:
        for row_chunk in chunk(rows, batch_size):
            warehouse.insert_rows(udf_table, row_chunk)


@frozen
class UDF(Step, ABC):
    udf: UDFType
    catalog: "Catalog"
    partition_by: Optional[PartitionByType] = None
    parallel: Optional[int] = None
    workers: Union[bool, int] = False
    min_task_size: Optional[int] = None
    is_generator = False
    cache: bool = False

    @abstractmethod
    def create_udf_table(self, udf) -> "Table":
        """Method that creates a table where temp udf results will be saved"""

    def process_input_query(self, query: S) -> tuple[S, list["Table"]]:
        """Apply any necessary processing to the input query"""
        return query, []

    @abstractmethod
    def create_result_query(
        self, udf_table, query, udf
    ) -> tuple[QueryGeneratorFunc, list["sqlalchemy.Column"]]:
        """
        Method that should return query to fetch results from udf and columns
        to select
        """

    def udf_table_name(self) -> str:
        return "udf_" + _random_string(6)

    @property
    def custom_columns_created(self) -> dict[str, SQLType]:
        return {
            col_name: col_type
            for (col_name, col_type) in self.udf.output.items()
            if col_name not in DATASET_CORE_COLUMN_NAMES
        }

    def populate_udf_table(self, udf_table, query, udf) -> None:
        use_partitioning = self.partition_by is not None
        batching = udf.properties.get_batching(use_partitioning)
        workers = self.workers
        if (
            not workers
            and os.environ.get("DVCX_DISTRIBUTED")
            and os.environ.get("DVCX_SETTINGS_WORKERS")
        ):
            # Enable distributed processing by default if the module is available,
            # and a default number of workers is provided.
            workers = True

        processes = determine_processes(self.parallel)

        try:
            if workers:
                from dvcx.catalog.loader import get_distributed_class

                distributor = get_distributed_class(min_task_size=self.min_task_size)
                distributor(
                    udf,
                    self.catalog,
                    udf_table,
                    query,
                    workers,
                    processes,
                    is_generator=self.is_generator,
                    use_partitioning=use_partitioning,
                    cache=self.cache,
                )
            elif processes:
                # Parallel processing (faster for more CPU-heavy UDFs)
                udf_info = {
                    "udf": udf,
                    "catalog_init": self.catalog.get_init_params(),
                    "id_generator_clone_params": (
                        self.catalog.id_generator.clone_params()
                    ),
                    "metastore_clone_params": self.catalog.metastore.clone_params(),
                    "warehouse_clone_params": self.catalog.warehouse.clone_params(),
                    "table": udf_table,
                    "query": query,
                    "batching": batching,
                    "processes": processes,
                    "is_generator": self.is_generator,
                    "cache": self.cache,
                }
                process_data = dumps(udf_info, recurse=True)
                # Run the UDFDispatcher in another process to avoid needing
                # if __name__ == '__main__': in user scripts
                dvcx_exec_path = os.environ.get("DVCX_EXEC_PATH", "dvcx")
                result = subprocess.run(
                    [dvcx_exec_path, "--internal-run-udf"],  # noqa: S603
                    input=process_data,
                    check=False,
                )
                if result.returncode != 0:
                    raise RuntimeError("UDF Execution Failed!")
            else:
                # Otherwise process single-threaded (faster for smaller UDFs)
                # Optionally instantiate the UDF instance if a class is provided.
                if isinstance(udf, UDFFactory):
                    udf = udf()

                udf_inputs = batching(
                    self.catalog.warehouse.dataset_select_paginated, query
                )
                udf_results = (
                    udf(
                        self.catalog,
                        row,
                        is_generator=self.is_generator,
                        cache=self.cache,
                    )
                    for row in udf_inputs
                )
                process_udf_outputs(self.catalog.warehouse, udf_table, udf_results, udf)
                self.catalog.warehouse.insert_rows_done(udf_table)
        except QueryScriptCancelError:
            self.catalog.warehouse.close()
            sys.exit(QUERY_SCRIPT_CANCELED_EXIT_CODE)
        except Exception:
            # Close any open database connections if an error is encountered
            self.catalog.warehouse.close()
            raise

    def create_partitions_table(self, query) -> "Table":
        """
        Create temporary table with group by partitions.
        """
        partition_by = self.partition_by
        if not isinstance(partition_by, Sequence):
            partition_by = [partition_by]

        # create table with partitions
        tbl = self.catalog.warehouse.create_udf_table(
            self.udf_table_name(), partition_columns()
        )

        # fill table with partitions
        cols = [
            query.selected_columns.id,
            f.dense_rank().over(order_by=partition_by).label(PARTITION_COLUMN_ID),
        ]
        self.catalog.warehouse.db.execute(
            tbl.insert().from_select(cols, query.with_only_columns(cols))
        )

        return tbl

    def clone(self, partition_by: Optional[PartitionByType] = None):
        if partition_by is not None:
            return self.__class__(
                self.udf,
                self.catalog,
                partition_by=partition_by,
                parallel=self.parallel,
                workers=self.workers,
                min_task_size=self.min_task_size,
            )
        return self.__class__(self.udf, self.catalog)

    def apply(self, query_generator):
        query = query_generator.select()
        temp_tables = []

        # Apply partitioning if needed.
        if self.partition_by is not None:
            partition_tbl = self.create_partitions_table(query)
            temp_tables.append(partition_tbl.name)

            subq = query.subquery()
            query = (
                sqlalchemy.select(*subq.c)
                .select_from(subq)
                .outerjoin(partition_tbl, partition_tbl.c.id == subq.c.id)
                .add_columns(*partition_columns())
            )

        if isinstance(self.udf, UDFClassWrapper):
            udf = self.udf()
        else:
            udf = self.udf

        query, tables = self.process_input_query(query)
        for t in tables:
            temp_tables.append(t.name)
        udf_table = self.create_udf_table(udf)
        temp_tables.append(udf_table.name)
        self.populate_udf_table(udf_table, query, udf)
        q, cols = self.create_result_query(udf_table, query, udf)

        return step_result(q, cols, temp_table_names=temp_tables)


@frozen
class UDFSignal(UDF):
    is_generator = False

    def create_udf_table(self, udf) -> "Table":
        udf_output_columns = [
            sqlalchemy.Column(col_name, col_type)
            for (col_name, col_type) in udf.output.items()
        ]

        return self.catalog.warehouse.create_udf_table(
            self.udf_table_name(), udf_output_columns
        )

    def create_pre_udf_table(self, query: S) -> "Table":
        columns = [
            sqlalchemy.Column(c.name, c.type)
            for c in query.selected_columns
            if c.name != "id"
        ]
        table = self.catalog.warehouse.create_udf_table(self.udf_table_name(), columns)
        select_q = query.with_only_columns(
            [c for c in query.selected_columns if c.name != "id"]
        )

        # if there is order by clause we need row_number to preserve order
        # if there is no order by clause we still need row_number to generate
        # unique ids as uniqueness is important for this table
        select_q = select_q.add_columns(
            f.row_number().over(order_by=select_q._order_by_clauses).label("id")
        )

        self.catalog.warehouse.db.execute(
            table.insert().from_select(select_q.selected_columns, select_q)
        )
        return table

    def process_input_query(self, query: S) -> tuple[S, list["Table"]]:
        if os.getenv("DVCX_DISABLE_QUERY_CACHE", "") not in ("", "0"):
            return query, []
        table = self.create_pre_udf_table(query)
        q = sqlalchemy.select(table.c).select_from(table)
        if query._order_by_clauses:
            # we are adding ordering only if it's explicitly added by user in
            # query part before adding signals
            q = q.order_by(table.c.id)
        return q, [table]

    def create_result_query(
        self, udf_table, query, udf
    ) -> tuple[QueryGeneratorFunc, list["sqlalchemy.Column"]]:
        subq = query.subquery()
        original_cols = [c for c in subq.c if c.name not in partition_col_names]

        # new signal columns that are added to udf_table
        signal_cols = [c for c in udf_table.c if c.name != "id"]
        signal_name_cols = {c.name: c for c in signal_cols}
        cols = signal_cols

        def q(*columns):
            cols1 = []
            cols2 = []
            for c in columns:
                if c.name in partition_col_names:
                    continue
                cols.append(signal_name_cols.get(c.name, c))
                if c.name in signal_name_cols.keys():
                    cols2.append(c)
                else:
                    cols1.append(c)

            if cols2:
                res = (
                    sqlalchemy.select(*cols1)
                    .select_from(subq)
                    .outerjoin(udf_table, udf_table.c.id == subq.c.id)
                    .add_columns(*cols2)
                )
            else:
                res = sqlalchemy.select(*cols1).select_from(subq)

            if query._order_by_clauses:
                # if ordering is used in query part before adding signals, we
                # will have it as order by id from select from pre-created udf table
                res = res.order_by(subq.c.id)

            if self.partition_by is not None:
                subquery = res.subquery()
                res = sqlalchemy.select(*subquery.c).select_from(subquery)

            return res

        return q, [*original_cols, *cols]


@frozen
class RowGenerator(UDF):
    """Extend dataset with new rows."""

    is_generator = True

    def create_udf_table(self, udf) -> "Table":
        table_name = self.udf_table_name()
        if isinstance(udf, UDFFactory):
            udf = udf()

        custom_udf_output_columns = [
            sqlalchemy.Column(col_name, col_type)
            for (col_name, col_type) in udf.output.items()
            if col_name not in DATASET_CORE_COLUMN_NAMES
        ]

        return self.catalog.warehouse.create_dataset_rows_table(
            table_name,
            custom_columns=custom_udf_output_columns,
            if_not_exists=False,
        )

    def create_result_query(
        self, udf_table, query, udf
    ) -> tuple[QueryGeneratorFunc, list["sqlalchemy.Column"]]:
        if not query._order_by_clauses:
            # if we are not selecting all rows in UDF, we need to ensure that
            # we get the same rows as we got as inputs of UDF since selecting
            # without ordering can be non deterministic in some databases
            c = query.selected_columns
            query = query.order_by(c.source, c.parent, c.name, c.version, c.etag)

        udf_table_query = udf_table.select().subquery()
        udf_table_cols = [label(c.name, c) for c in udf_table_query.columns]

        def q(*columns):
            names = {c.name for c in columns}
            # Columns for the generated table.
            cols = [c for c in udf_table_cols if c.name in names]
            return sqlalchemy.select(*cols).select_from(udf_table_query)

        return q, udf_table_query.columns


@frozen
class SQLClause(Step, ABC):
    def apply(self, query_generator):
        query = query_generator.select()
        new_query = self.apply_sql_clause(query)

        def q(*columns):
            return new_query.with_only_columns(*columns)

        return step_result(q, new_query.selected_columns)

    @abstractmethod
    def apply_sql_clause(self, query):
        pass


@frozen
class SQLSelect(SQLClause):
    args: tuple[ColumnElement, ...]

    def apply_sql_clause(self, query):
        subquery = query.subquery()

        args = [subquery.c[str(c)] if isinstance(c, (str, C)) else c for c in self.args]
        if not args:
            args = subquery.c

        return sqlalchemy.select(*args).select_from(subquery)


@frozen
class SQLSelectExcept(SQLClause):
    args: tuple[str, ...]

    def apply_sql_clause(self, query):
        subquery = query.subquery()
        names = set(self.args)
        args = [c for c in subquery.c if c.name not in names]
        return sqlalchemy.select(*args).select_from(subquery)


@frozen
class SQLMutate(SQLClause):
    args: tuple[ColumnElement, ...]

    def apply_sql_clause(self, query):
        subquery = query.subquery()
        return sqlalchemy.select(*subquery.c, *self.args).select_from(subquery)


@frozen
class SQLFilter(SQLClause):
    expressions: tuple[ColumnElement, ...]

    def __and__(self, other):
        return self.__class__(self.expressions + other)

    def apply_sql_clause(self, query):
        return query.filter(*self.expressions)


@frozen
class SQLOrderBy(SQLClause):
    args: tuple[ColumnElement, ...]

    def apply_sql_clause(self, query):
        return query.order_by(*self.args)


@frozen
class SQLLimit(SQLClause):
    n: int

    def apply_sql_clause(self, query):
        return query.limit(self.n)


@frozen
class SQLOffset(SQLClause):
    offset: int

    def apply_sql_clause(self, query: "GenerativeSelect"):
        return query.offset(self.offset)


@frozen
class SQLCount(SQLClause):
    def apply_sql_clause(self, query):
        return sqlalchemy.select(f.count(1)).select_from(query.subquery())


@frozen
class SQLUnion(Step):
    query1: "DatasetQuery"
    query2: "DatasetQuery"

    def apply(self, query_generator):
        q1 = self.query1.apply_steps().select().subquery()
        q2 = self.query2.apply_steps().select().subquery()
        columns1, columns2 = fill_columns(q1.columns, q2.columns)

        def q(*columns):
            names = {c.name for c in columns}
            col1 = [c for c in columns1 if c.name in names]
            col2 = [c for c in columns2 if c.name in names]
            res = (
                sqlalchemy.select(*col1)
                .select_from(q1)
                .union_all(sqlalchemy.select(*col2).select_from(q2))
            )

            subquery = res.subquery()
            return sqlalchemy.select(*subquery.c).select_from(subquery)

        return step_result(
            q,
            columns1,
            dependencies=self.query1.dependencies | self.query2.dependencies,
        )


@frozen
class SQLJoin(Step):
    query1: "DatasetQuery"
    query2: "DatasetQuery"
    predicates: Union[JoinPredicateType, tuple[JoinPredicateType, ...]]
    inner: bool
    rname: str

    def validate_expression(self, exp: ColumnElement, q1, q2):
        """
        Checking if columns used in expression actually exist in left / right
        part of the join
        """
        for c in exp.get_children():
            if isinstance(c, ColumnClause):
                q1_c = q1.c.get(c.name)
                q2_c = q2.c.get(c.name)

                if c.table.name == q1.name and q1_c is None:
                    raise ValueError(
                        f"Column {c.name} was not found in left part of the join"
                    )

                elif c.table.name == q2.name and q2_c is None:
                    raise ValueError(
                        f"Column {c.name} was not found in right part of the join"
                    )
                elif c.table.name not in [q1.name, q2.name]:
                    raise ValueError(
                        f"Column {c.name} was not found in left or right"
                        " part of the join"
                    )
                else:
                    continue
            else:
                self.validate_expression(c, q1, q2)

    def apply(self, query_generator):
        q1 = self.query1.apply_steps().select().subquery(self.query1.table.name)
        q2 = self.query2.apply_steps().select().subquery(self.query2.table.name)

        q1_columns = list(q1.c)
        q1_column_names = {c.name for c in q1_columns}
        q2_columns = [
            c
            if c.name not in q1_column_names and c.name != "id"
            else c.label(self.rname.format(name=c.name))
            for c in q2.c
        ]

        res_columns = q1_columns + q2_columns
        predicates = (
            (self.predicates,)
            if not isinstance(self.predicates, tuple)
            else self.predicates
        )

        expressions = []
        for p in predicates:
            if isinstance(p, ColumnClause):
                expressions.append(self.query1.c(p.name) == self.query2.c(p.name))
            elif isinstance(p, str):
                expressions.append(self.query1.c(p) == self.query2.c(p))
            elif isinstance(p, ColumnElement):
                expressions.append(p)
            else:
                raise ValueError(f"Unsupported predicate {p} for join expression")

        if not expressions:
            raise ValueError("Missing predicates")

        join_expression = sqlalchemy.and_(*expressions)
        self.validate_expression(join_expression, q1, q2)

        def q(*columns):
            join_query = sqlalchemy.join(
                q1,
                q2,
                join_expression,
                isouter=not self.inner,
            )

            res = sqlalchemy.select(columns).select_from(join_query)
            subquery = res.subquery()
            return sqlalchemy.select(*subquery.c).select_from(subquery)

        return step_result(
            q,
            res_columns,
            dependencies=self.query1.dependencies | self.query2.dependencies,
        )


@frozen
class GroupBy(Step):
    """Group rows by a specific column."""

    cols: PartitionByType

    def clone(self):
        return self.__class__(self.cols)

    def apply(self, query_generator):
        query = query_generator.select()
        grouped_query = query.group_by(*self.cols)

        def q(*columns):
            return grouped_query.with_only_columns(*columns)

        return step_result(q, grouped_query.selected_columns)


def fill_columns(
    *column_iterables: Iterable[ColumnElement],
) -> list[list[ColumnElement]]:
    column_dicts = [{c.name: c for c in columns} for columns in column_iterables]
    combined_columns = {n: c for col_dict in column_dicts for n, c in col_dict.items()}

    result: list[list[ColumnElement]] = [[] for _ in column_dicts]
    for n in combined_columns:
        col = next(col_dict[n] for col_dict in column_dicts if n in col_dict)
        for col_dict, out in zip(column_dicts, result):
            if n in col_dict:
                out.append(col_dict[n])
            else:
                # Cast the NULL to ensure all columns are aware of their type
                # Label it to ensure it's aware of its name
                out.append(sqlalchemy.cast(sqlalchemy.null(), col.type).label(n))
    return result


@attrs.define
class ResultIter:
    _row_iter: Iterable[Any]
    columns: list[str]

    def __iter__(self):
        yield from self._row_iter


class DatasetQuery:
    def __init__(
        self,
        path: str = "",
        name: str = "",
        version: Optional[int] = None,
        catalog: Optional["Catalog"] = None,
        client_config=None,
        recursive: Optional[bool] = True,
    ):
        self.steps: list["Step"] = []
        self.catalog = catalog or get_catalog(client_config=client_config)
        self._chunk_index: Optional[int] = None
        self._chunk_total: Optional[int] = None
        self.temp_table_names: list[str] = []
        self.dependencies: set[DatasetDependencyType] = set()
        self.table = self.get_table()
        self.starting_step: StartingStep
        self.name: Optional[str] = None
        self.version: Optional[int] = None

        if path:
            self.starting_step = IndexingStep(
                path, self.catalog, {"client_config": client_config}, recursive
            )
        elif name:
            version = version or self.catalog.get_dataset(name).latest_version
            self.starting_step = QueryStep(self.catalog, name, version)
            # attaching to specific dataset
            self.name = name
            self.version = version
        else:
            raise ValueError("must provide path or name")

    def __iter__(self):
        return iter(self.results())

    def __or__(self, other):
        return self.union(other)

    @staticmethod
    def get_table() -> "Table":
        table_name = "".join(
            random.choice(string.ascii_letters)  # noqa: S311
            for _ in range(16)
        )
        return sqlalchemy.table(table_name)

    @staticmethod
    def delete(
        name: str, version: Optional[int] = None, catalog: Optional["Catalog"] = None
    ) -> None:
        catalog = catalog or get_catalog()
        version = version or catalog.get_dataset(name).latest_version
        catalog.remove_dataset(name, version)

    @property
    def attached(self) -> bool:
        """
        DatasetQuery is considered "attached" to underlying dataset if it represents
        it completely. If this is the case, name and version of underlying dataset
        will be defined.
        DatasetQuery instance can become attached in two scenarios:
            1. ds = DatasetQuery(name="dogs", version=1) -> ds is attached to dogs
            2. ds = ds.save("dogs", version=1) -> ds is attached to dogs dataset
        It can move to detached state if filter or similar methods are called on it,
        as then it no longer 100% represents underlying datasets.
        """
        return self.name is not None and self.version is not None

    def c(self, name: Union[C, str]) -> C:
        col = sqlalchemy.column(name) if isinstance(name, str) else name
        col.table = self.table
        return col

    def apply_steps(self) -> QueryGenerator:
        """
        Apply the steps in the query and return the resulting
        sqlalchemy.SelectBase.
        """
        query = self.clone()

        index = os.getenv("DVCX_QUERY_CHUNK_INDEX", self._chunk_index)
        total = os.getenv("DVCX_QUERY_CHUNK_TOTAL", self._chunk_total)

        if index is not None and total is not None:
            index, total = int(index), int(total)  # os.getenv returns str

            if not (0 <= index < total):
                raise ValueError("chunk index must be between 0 and total")

            # Prepend the chunk filter to the step chain.
            query = query.filter(C.random % total == index)
            query.steps = query.steps[-1:] + query.steps[:-1]

        result = query.starting_step.apply()
        group_by = None
        self.temp_table_names.extend(result.temp_table_names)
        self.dependencies.update(result.dependencies)

        for step in query.steps:
            if isinstance(step, GroupBy):
                if group_by is not None:
                    raise TypeError("only one group_by allowed")
                group_by = step
                continue

            result = step.apply(
                result.query_generator
            )  # a chain of steps linked by results
            self.temp_table_names.extend(result.temp_table_names)
            self.dependencies.update(result.dependencies)

        if group_by:
            result = group_by.apply(result.query_generator)
            self.temp_table_names.extend(result.temp_table_names)
            self.dependencies.update(result.dependencies)

        return result.query_generator

    def cleanup(self) -> None:
        self.catalog.warehouse.clone().cleanup_temp_tables(self.temp_table_names)
        self.catalog.metastore.clone().cleanup_temp_tables(self.temp_table_names)
        self.temp_table_names = []

    def results(self, row_factory=None, **kwargs):
        with self.as_iterable(**kwargs) as result:
            if row_factory:
                cols = result.columns
                return [row_factory(cols, r) for r in result]
            else:
                return list(result)

    @contextlib.contextmanager
    def as_iterable(self, **kwargs) -> Iterator[ResultIter]:
        try:
            query = self.apply_steps().select()
            selected_columns = [c.name for c in query.columns]
            yield ResultIter(
                self.catalog.warehouse.dataset_rows_select(query, **kwargs),
                selected_columns,
            )
        finally:
            self.cleanup()

    def extract(
        self, *params: UDFParamSpec, workers=ASYNC_WORKERS, **kwargs
    ) -> Iterable[tuple]:
        """
        Extract columns from each row in the query.

        Returns an iterable of tuples matching the given params.

        To ensure prompt resource cleanup, it is recommended to wrap this
        with contextlib.closing().
        """
        actual_params = [normalize_param(p) for p in params]
        try:
            query = self.apply_steps().select()

            def row_iter() -> Iterable[DatasetRow]:
                # warehouse isn't threadsafe, we need to clone() it
                # in the thread that uses the results
                db = self.catalog.warehouse.clone()
                yield from db.dataset_select_paginated(
                    query, limit=query._limit, order_by=query._order_by_clauses
                )

            async def get_params(row: DatasetRow) -> tuple:
                return tuple(
                    [
                        await p.get_value_async(self.catalog, row, mapper, **kwargs)
                        for p in actual_params
                    ]
                )

            MapperCls = OrderedMapper if query._order_by_clauses else AsyncMapper  # noqa: N806
            mapper = MapperCls(get_params, row_iter(), workers=workers)
            for params in mapper.iterate():
                yield params
        finally:
            self.cleanup()

    def to_records(self) -> list[dict]:
        with self.as_iterable() as result:
            cols = result.columns
            return [dict(zip(cols, row)) for row in result]

    def to_pandas(self):
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError(
                "Missing required dependency pandas for DatasetQuery.to_pandas()\n"
                "To install run:\n\n"
                "  pip install 'dvcx[pandas]'\n"
            ) from exc

        records = self.to_records()
        return pd.DataFrame.from_records(records)

    def shuffle(self) -> "DatasetQuery":
        # ToDo: implement shaffle based on seed and/or generating random column
        return self.order_by(C.random)

    def show(self, limit=20) -> None:
        df = self.limit(limit).to_pandas()
        no_footer = re.sub(r"\n\[\d+ rows x \d+ columns\]$", "", str(df))
        print(no_footer.rstrip(" \n"))
        if len(df) == limit:
            print(f"[limited by {limit} objects]")

    def clone(self, new_table=True) -> "Self":
        obj = copy(self)
        obj.steps = obj.steps.copy()
        if new_table:
            obj.table = self.get_table()
        return obj

    @detach
    def select(self, *args, **kwargs) -> "Self":
        """
        Select the given columns or expressions using a subquery.

        If used with no arguments, this simply creates a subquery and
        select all columns from it.

        Note that the `save` function expects default dataset columns to
        be present. This function is meant to be followed by a call to
        `results` if used to exclude any default columns.

        Example:
            >>> ds.select(C.name, C.size * 10).results()
            >>> ds.select(C.name, size10x=C.size * 10).order_by(C.size10x).results()
        """
        named_args = [v.label(k) for k, v in kwargs.items()]
        query = self.clone()
        query.steps.append(SQLSelect((*args, *named_args)))
        return query

    @detach
    def select_except(self, *args) -> "Self":
        """
        Exclude certain columns from this query using a subquery.

        Note that the `save` function expects default dataset columns to
        be present. This function is meant to be followed by a call to
        `results` if used to exclude any default columns.

        Example:
            >>> (
            ...     ds.mutate(size10x=C.size * 10)
            ...     .order_by(C.size10x)
            ...     .select_except(C.size10x)
            ...     .results()
            ... )
        """

        if not args:
            raise TypeError("select_except expected at least 1 argument, got 0")
        query_args = [c if isinstance(c, str) else c.name for c in args]
        query = self.clone()
        query.steps.append(SQLSelectExcept(query_args))  # type: ignore [arg-type]
        return query

    @detach
    def select_default(self) -> "Self":
        """
        Select only the default dataset columns using a subquery.

        This assumes that none of the default dataset columns have
        already been excluded from this query. This is useful if you've
        added columns with `mutate` or `select` calls for filtering but
        only want the default columns in the final output.

        Example:
            >>> (
            ...     ds.mutate(size10x=C.size * 10)
            ...     .order_by(C.size10x)
            ...     .select_default()
            ...     .results()
            ... )
        """
        query = self.clone()
        query.steps.append(SQLSelect((*DATASET_CORE_COLUMN_NAMES,)))
        return query

    @detach
    def mutate(self, *args, **kwargs) -> "Self":
        """
        Add new columns to this query.

        This function selects all existing columns from this query and
        adds in the new columns specified.

        Example:
            >>> ds.mutate(size10x=C.size * 10).order_by(C.size10x).results()
        """
        query_args = [v.label(k) for k, v in dict(args, **kwargs).items()]
        query = self.clone()
        query.steps.append(SQLMutate((*query_args,)))
        return query

    @detach
    def filter(self, *args) -> "Self":
        query = self.clone(new_table=False)
        steps = query.steps
        if steps and isinstance(steps[-1], SQLFilter):
            steps[-1] = steps[-1] & args
        else:
            steps.append(SQLFilter(args))
        return query

    @detach
    def order_by(self, *args) -> "Self":
        query = self.clone(new_table=False)
        query.steps.append(SQLOrderBy(args))
        return query

    @detach
    def limit(self, n: int) -> "Self":
        query = self.clone(new_table=False)
        query.steps.append(SQLLimit(n))
        return query

    @detach
    def offset(self, offset: int) -> "Self":
        query = self.clone(new_table=False)
        query.steps.append(SQLOffset(offset))
        return query

    def count(self) -> int:
        query = self.clone()
        query.steps.append(SQLCount())
        return query.results()[0][0]

    def sum(self, col: ColumnElement):
        query = self.clone()
        query.steps.append(SQLSelect((f.sum(col),)))
        return query.results()[0][0]

    def avg(self, col: ColumnElement):
        query = self.clone()
        query.steps.append(SQLSelect((f.avg(col),)))
        return query.results()[0][0]

    def min(self, col: ColumnElement):
        query = self.clone()
        query.steps.append(SQLSelect((f.min(col),)))
        return query.results()[0][0]

    def max(self, col: ColumnElement):
        query = self.clone()
        query.steps.append(SQLSelect((f.max(col),)))
        return query.results()[0][0]

    @detach
    def group_by(self, *cols: ColumnElement) -> "Self":
        query = self.clone()
        query.steps.append(GroupBy(cols))
        return query

    @detach
    def union(self, dataset_query: "DatasetQuery") -> "Self":
        left = self.clone()
        right = dataset_query.clone()
        new_query = self.clone()
        new_query.steps = [SQLUnion(left, right)]
        return new_query

    @detach
    def join(
        self,
        dataset_query: "DatasetQuery",
        predicates: Union[JoinPredicateType, Sequence[JoinPredicateType]],
        inner=False,
        rname="{name}_right",
    ) -> "Self":
        left = self.clone(new_table=False)
        if self.table.name == dataset_query.table.name:
            # for use case where we join with itself, e.g dogs.join(dogs, "name")
            right = dataset_query.clone(new_table=True)
        else:
            right = dataset_query.clone(new_table=False)

        new_query = self.clone()
        predicates = (
            predicates
            if isinstance(predicates, (str, ColumnClause, ColumnElement))
            else tuple(predicates)
        )
        new_query.steps = [SQLJoin(left, right, predicates, inner, rname)]
        return new_query

    @detach
    def chunk(self, index: int, total: int) -> "Self":
        """Split a query into smaller chunks for e.g. parallelization.
        Example:
            >>> query = DatasetQuery(...)
            >>> chunk_1 = query._chunk(0, 2)
            >>> chunk_2 = query._chunk(1, 2)
        Note:
            Bear in mind that `index` is 0-indexed but `total` isn't.
            Use 0/3, 1/3 and 2/3, not 1/3, 2/3 and 3/3.
        """
        query = self.clone()
        query._chunk_index, query._chunk_total = index, total
        return query

    @detach
    def add_signals(
        self,
        udf: UDFType,
        parallel: Optional[int] = None,
        workers: Union[bool, int] = False,
        min_task_size: Optional[int] = None,
        partition_by: Optional[PartitionByType] = None,
        cache: bool = False,
    ) -> "Self":
        """
        Adds one or more signals based on the results from the provided UDF.

        Parallel can optionally be specified as >= 1 for parallel processing with a
        specific number of processes, or set to -1 for the default of
        the number of CPUs (cores) on the current machine.

        For distributed processing with the appropriate distributed module installed,
        workers can optionally be specified as >= 1 for a specific number of workers,
        or set to True for the default of all nodes in the cluster.
        As well, a custom minimum task size (min_task_size) can be provided to send
        at least that minimum number of rows to each distributed worker, mostly useful
        if there are a very large number of small tasks to process.
        """
        query = self.clone()
        query.steps.append(
            UDFSignal(
                udf,
                self.catalog,
                partition_by=partition_by,
                parallel=parallel,
                workers=workers,
                min_task_size=min_task_size,
                cache=cache,
            )
        )
        return query

    @detach
    def subtract(self, dq: "DatasetQuery") -> "Self":
        query = self.clone()
        query.steps.append(Subtract(dq, self.catalog))
        return query

    @detach
    def changed(self, dq: "DatasetQuery") -> "Self":
        query = self.clone()
        query.steps.append(Changed(dq, self.catalog))
        return query

    @detach
    def generate(
        self,
        udf: UDFType,
        parallel: Optional[int] = None,
        workers: Union[bool, int] = False,
        min_task_size: Optional[int] = None,
        partition_by: Optional[PartitionByType] = None,
        cache: bool = False,
    ) -> "Self":
        query = self.clone()
        steps = query.steps
        steps.append(
            RowGenerator(
                udf,
                self.catalog,
                partition_by=partition_by,
                parallel=parallel,
                workers=workers,
                min_task_size=min_task_size,
                cache=cache,
            )
        )
        return query

    def _add_dependencies(self, dataset: "DatasetRecord", version: int):
        for dependency in self.dependencies:
            if isinstance(dependency, tuple):
                # dataset dependency
                ds_dependency_name, ds_dependency_version = dependency
                self.catalog.metastore.add_dataset_dependency(
                    dataset.name,
                    version,
                    ds_dependency_name,
                    ds_dependency_version,
                )
            else:
                # storage dependency - its name is a valid StorageURI
                storage = self.catalog.get_storage(dependency)
                self.catalog.metastore.add_storage_dependency(
                    StorageURI(dataset.name),
                    version,
                    storage.uri,
                    storage.timestamp_str,
                )

    def save(
        self, name: str, version: Optional[int] = None, **kwargs
    ) -> "DatasetQuery":
        """Save the query as a dataset."""
        try:
            if version and self.catalog.get_dataset(name).has_version(version):
                raise RuntimeError(f"Dataset {name} already has version {version}")
        except DatasetNotFoundError:
            pass

        try:
            query = self.apply_steps()

            missing_default_columns = [
                c_name
                for c_name in DATASET_CORE_COLUMN_NAMES
                if c_name not in [c.name for c in query.columns]
            ]
            if missing_default_columns:
                raise RuntimeError(
                    'Missing default columns from final query: '
                    f'{", ".join(missing_default_columns)}'
                )

            custom_columns: list["sqlalchemy.Column"] = [
                sqlalchemy.Column(col.name, col.type)
                for col in query.columns
                if col.name not in DATASET_CORE_COLUMN_NAMES
            ]

            dataset = self.catalog.create_dataset(
                name,
                version=version,
                custom_columns=custom_columns,
                **kwargs,
            )
            version = version or dataset.latest_version

            dr = self.catalog.warehouse.dataset_rows(dataset)

            # Exclude the id column and let the db create it to avoid unique
            # constraint violations, and parent_id is not used in datasets.
            cols = [
                col.name
                for col in dr.get_table().c
                if col.name not in ("id", "parent_id")
            ]

            q = query.exclude(("id", "parent_id"))

            if q._order_by_clauses:
                # ensuring we have id sorted by order by clause if it exists in a query
                q = q.add_columns(
                    f.row_number().over(order_by=q._order_by_clauses).label("id")
                )
                cols.append("id")

            self.catalog.warehouse.db.execute(
                sqlalchemy.insert(dr.get_table()).from_select(cols, q),
                **kwargs,
            )

            self.catalog.metastore.update_dataset_status(
                dataset, DatasetStatus.COMPLETE, version=version
            )

            self._add_dependencies(dataset, version)  # type: ignore [arg-type]
        finally:
            self.cleanup()

        return DatasetQuery(name=name, version=version, catalog=self.catalog)


def query_wrapper_save(dataset_query: DatasetQuery) -> DatasetQuery:
    """
    Wrapper function that wraps the last statement of user query script for creating
    new dataset
    Last statement MUST be instance of DatasetQuery, otherwise script exits with
    error code 10
    """
    if not isinstance(dataset_query, DatasetQuery):
        sys.exit(QUERY_SCRIPT_INVALID_LAST_STATEMENT_EXIT_CODE)

    if isinstance(dataset_query, DatasetQuery):
        if dataset_query.attached:
            dataset_query.catalog.warehouse.return_ds_hook(
                dataset_query.name,  # type: ignore [arg-type]
                dataset_query.version,  # type: ignore [arg-type]
            )
        else:
            ds_name = dataset_query.catalog.generate_query_dataset_name()
            dataset_query.catalog.warehouse.return_ds_hook(ds_name, 1)
            dataset_query.save(ds_name)

    return dataset_query


def query_wrapper_print(dataset_query: DatasetQuery) -> DatasetQuery:
    """
    Wrapper function that wraps the last statement of user query script for printing
    results in console.
    Last statement MUST be instance of DatasetQuery, otherwise script exits with
    error code 10
    """

    def _json_serialize(obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        return obj

    if not isinstance(dataset_query, DatasetQuery):
        sys.exit(QUERY_SCRIPT_INVALID_LAST_STATEMENT_EXIT_CODE)

    try:
        preview_args: dict[str, Any] = json.loads(
            os.getenv("DVCX_QUERY_PREVIEW_ARGS", "")
        )
    except ValueError:
        preview_args = {}

    columns = preview_args.get("columns") or []
    if columns:
        columns.insert(0, "id")

    preview_query = (
        dataset_query.select(*columns)
        .limit(preview_args.get("limit", 10))
        .offset(preview_args.get("offset", 0))
    )
    records = json.dumps(preview_query.to_records(), default=_json_serialize)
    print("__ds_records__", records, "__ds_records__", sep="")
    return dataset_query


def _random_string(length: int) -> str:
    return "".join(
        random.choice(string.ascii_letters + string.digits)  # noqa: S311
        for i in range(length)
    )
