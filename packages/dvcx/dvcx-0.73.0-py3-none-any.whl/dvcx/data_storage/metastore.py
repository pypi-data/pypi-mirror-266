import copy
import hashlib
import json
import logging
import posixpath
from abc import ABC, abstractmethod
from collections.abc import Iterator
from datetime import datetime, timezone
from functools import cached_property, reduce
from itertools import groupby
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Table,
    Text,
    UniqueConstraint,
    select,
)
from sqlalchemy.sql import func

from dvcx.data_storage.serializer import Serializable
from dvcx.dataset import DatasetDependency, DatasetRecord, DatasetVersion
from dvcx.dataset import Status as DatasetStatus
from dvcx.error import DatasetNotFoundError, StorageNotFoundError
from dvcx.sql.types import SQLType
from dvcx.storage import Status as StorageStatus
from dvcx.storage import Storage, StorageURI
from dvcx.utils import is_expired

if TYPE_CHECKING:
    from sqlalchemy.schema import SchemaItem

    from dvcx.data_storage import AbstractIDGenerator, schema
    from dvcx.data_storage.db_engine import DatabaseEngine


logger = logging.getLogger("dvcx")


class AbstractMetastore(ABC, Serializable):
    """
    Abstract Metastore class.
    This manages the storing, searching, and retrieval of indexed metadata.
    """

    uri: StorageURI
    partial_id: Optional[int]

    schema: "schema.Schema"
    storage_class: type[Storage] = Storage
    dataset_class: type[DatasetRecord] = DatasetRecord
    dependency_class: type[DatasetDependency] = DatasetDependency

    def __init__(
        self,
        uri: StorageURI = StorageURI(""),
        partial_id: Optional[int] = None,
    ):
        self.uri = uri
        self.partial_id: Optional[int] = partial_id

    @abstractmethod
    def clone(
        self, uri: StorageURI = StorageURI(""), partial_id: Optional[int] = None
    ) -> "AbstractMetastore":
        """Clones AbstractMetastore implementation for some Storage input."""

    def init(self, uri: StorageURI, partial_id: int) -> None:  # noqa: B027
        """Initialize metastore."""

    def close(self) -> None:  # noqa: B027
        """Closes any active database or HTTP connections."""

    def cleanup_temp_tables(self, temp_table_names: list[str]):  # noqa: B027
        """Cleanup temp tables."""

    def cleanup_for_tests(self):  # noqa: B027
        """Cleanup for tests."""

    #
    # Storages
    #

    @abstractmethod
    def create_storage_if_not_registered(self, uri: StorageURI) -> None:
        """Saves new storage if it doesn't exist in database."""

    @abstractmethod
    def register_storage_for_indexing(
        self,
        uri: StorageURI,
        force_update: bool = True,
        prefix: str = "",
    ) -> tuple[Storage, bool, bool, Optional[int]]:
        """
        Prepares storage for indexing operation.
        This method should be called before index operation is started
        It returns:
            - storage, prepared for indexing
            - boolean saying if indexing is needed
            - boolean saying if indexing is currently pending (running)
            - boolean saying if this storage is newly created
        """

    @abstractmethod
    def find_stale_storages(self) -> None:
        """
        Finds all pending storages for which the last inserted node has happened
        before STALE_HOURS_LIMIT hours, and marks it as STALE.
        """

    @abstractmethod
    def mark_storage_indexed(
        self,
        uri: StorageURI,
        status: int,
        ttl: int,
        end_time: Optional[datetime] = None,
        prefix: str = "",
        partial_id: int = 0,
        error_message: str = "",
        error_stack: str = "",
    ) -> None:
        """
        Marks storage as indexed.
        This method should be called when index operation is finished.
        """

    @abstractmethod
    def mark_storage_not_indexed(self, uri: StorageURI) -> None:
        """
        Mark storage as not indexed.
        This method should be called when storage index is deleted.
        """

    @abstractmethod
    def update_last_inserted_at(self, uri: Optional[StorageURI] = None) -> None:
        """Updates last inserted datetime in bucket with current time."""

    @abstractmethod
    def get_all_storage_uris(self) -> Iterator[StorageURI]:
        """Returns all storage uris."""

    @abstractmethod
    def get_storage(self, uri: StorageURI) -> Storage:
        """
        Gets storage representation from database.
        E.g. if s3 is used as storage this would be s3 bucket data.
        """

    @abstractmethod
    def list_storages(self) -> list[Storage]:
        """Returns all storages."""

    @abstractmethod
    def mark_storage_pending(self, storage: Storage) -> Storage:
        """Marks storage as pending."""

    #
    # Partial Indexes
    #

    @abstractmethod
    def init_partial_id(self, uri: StorageURI) -> None:
        """Initializes partial id for given storage."""

    @abstractmethod
    def get_next_partial_id(self, uri: StorageURI) -> int:
        """Returns next partial id for given storage."""

    @abstractmethod
    def get_valid_partial_id(
        self, uri: StorageURI, prefix: str, raise_exc: bool = True
    ) -> Optional[int]:
        """Returns valid partial id for given storage."""

    @abstractmethod
    def get_last_partial_id(self, uri: StorageURI) -> Optional[int]:
        """Returns last partial id for given storage."""

    #
    # Datasets
    #

    @abstractmethod
    def create_dataset(
        self,
        name: str,
        status: int = DatasetStatus.CREATED,
        sources: Optional[list[str]] = None,
        query_script: str = "",
        custom_column_types: Optional[dict[str, Any]] = None,
        ignore_if_exists: bool = False,
    ) -> DatasetRecord:
        """Creates new dataset."""

    @abstractmethod
    def create_dataset_version(
        self,
        dataset: DatasetRecord,
        version: int,
        status: int = DatasetStatus.CREATED,
        sources: str = "",
        query_script: str = "",
        error_message: str = "",
        error_stack: str = "",
        script_output: str = "",
        created_at: Optional[datetime] = None,
        finished_at: Optional[datetime] = None,
        custom_column_types: Optional[dict[str, Any]] = None,
        ignore_if_exists: bool = False,
    ) -> DatasetRecord:
        """Creates new dataset version."""

    @abstractmethod
    def remove_dataset(self, dataset: DatasetRecord) -> None:
        """Removes dataset."""

    @abstractmethod
    def update_dataset(self, dataset: DatasetRecord, **kwargs) -> DatasetRecord:
        """Updates dataset fields."""

    @abstractmethod
    def update_dataset_version(
        self, dataset_version: DatasetVersion, **kwargs
    ) -> DatasetVersion:
        """Updates dataset version fields."""

    @abstractmethod
    def remove_dataset_version(
        self, dataset: DatasetRecord, version: int
    ) -> DatasetRecord:
        """
        Deletes one single dataset version.
        If it was last version, it removes dataset completely.
        """

    @abstractmethod
    def list_datasets(self) -> Iterator[DatasetRecord]:
        """Lists all datasets."""

    @abstractmethod
    def get_dataset(self, name: str) -> DatasetRecord:
        """Gets a single dataset by name."""

    @abstractmethod
    def update_dataset_status(
        self,
        dataset: DatasetRecord,
        status: int,
        version: Optional[int] = None,
        error_message="",
        error_stack="",
        script_output="",
    ) -> DatasetRecord:
        """Updates dataset status and appropriate fields related to status."""

    #
    # Dataset dependencies
    #

    def add_dependency(
        self,
        dependency: DatasetDependency,
        source_dataset_name: str,
        source_dataset_version: int,
    ) -> None:
        """Add dependency to dataset or storage."""
        if dependency.is_dataset:
            self.add_dataset_dependency(
                source_dataset_name,
                source_dataset_version,
                dependency.name,
                int(dependency.version),
            )
        else:
            self.add_storage_dependency(
                source_dataset_name,
                source_dataset_version,
                StorageURI(dependency.name),
                dependency.version,
            )

    @abstractmethod
    def add_storage_dependency(
        self,
        source_dataset_name: str,
        source_dataset_version: int,
        storage_uri: StorageURI,
        storage_timestamp_str: Optional[str] = None,
    ) -> None:
        """Adds storage dependency to dataset."""

    @abstractmethod
    def add_dataset_dependency(
        self,
        source_dataset_name: str,
        source_dataset_version: int,
        dataset_name: str,
        dataset_version: int,
    ) -> None:
        """Adds dataset dependency to dataset."""

    @abstractmethod
    def update_dataset_dependency_source(
        self,
        source_dataset: DatasetRecord,
        source_dataset_version: int,
        new_source_dataset: Optional[DatasetRecord] = None,
        new_source_dataset_version: Optional[int] = None,
    ) -> None:
        """Updates dataset dependency source."""

    @abstractmethod
    def get_direct_dataset_dependencies(
        self, dataset: DatasetRecord, version: int
    ) -> list[Optional[DatasetDependency]]:
        """Gets direct dataset dependencies."""

    @abstractmethod
    def remove_dataset_dependencies(
        self, dataset: DatasetRecord, version: Optional[int] = None
    ) -> None:
        """
        When we remove dataset, we need to clean up it's dependencies as well.
        """

    @abstractmethod
    def remove_dataset_dependants(
        self, dataset: DatasetRecord, version: Optional[int] = None
    ) -> None:
        """
        When we remove dataset, we need to clear its references in other dataset
        dependencies.
        """


class AbstractDBMetastore(AbstractMetastore):
    """
    Abstract Database Metastore class, to be implemented
    by any Database Adapters for a specific database system.
    This manages the storing, searching, and retrieval of indexed metadata,
    and has shared logic for all database systems currently in use.
    """

    PARTIALS_TABLE_NAME_PREFIX = "prt_"
    STORAGE_TABLE = "buckets"
    DATASET_TABLE = "datasets"
    DATASET_VERSION_TABLE = "datasets_versions"
    DATASET_DEPENDENCY_TABLE = "datasets_dependencies"

    id_generator: "AbstractIDGenerator"
    db: "DatabaseEngine"

    def __init__(
        self,
        id_generator: "AbstractIDGenerator",
        uri: StorageURI = StorageURI(""),
        partial_id: Optional[int] = None,
    ):
        self.id_generator = id_generator
        super().__init__(uri, partial_id)

    def close(self) -> None:
        """Closes any active database connections."""
        self.db.close()

    def cleanup_temp_tables(self, temp_table_names: list[str]):
        """Cleanup temp tables."""
        self.id_generator.delete_uris(temp_table_names)

    @classmethod
    def _buckets_columns(cls) -> list["SchemaItem"]:
        """Buckets (storages) table columns."""
        return [
            Column("id", Integer, primary_key=True, nullable=False),
            Column("uri", Text, nullable=False),
            Column("timestamp", DateTime(timezone=True)),
            Column("expires", DateTime(timezone=True)),
            Column("started_inserting_at", DateTime(timezone=True)),
            Column("last_inserted_at", DateTime(timezone=True)),
            Column("status", Integer, nullable=False),
            Column("error_message", Text, nullable=False, default=""),
            Column("error_stack", Text, nullable=False, default=""),
        ]

    @classmethod
    def _datasets_columns(cls) -> list["SchemaItem"]:
        """Datasets table columns."""
        return [
            Column("id", Integer, primary_key=True),
            Column("name", Text, nullable=False),
            Column("description", Text),
            Column("labels", JSON, nullable=True),
            Column("shadow", Boolean, nullable=False),
            Column("status", Integer, nullable=False),
            Column("created_at", DateTime(timezone=True)),
            Column("finished_at", DateTime(timezone=True)),
            Column("error_message", Text, nullable=False, default=""),
            Column("error_stack", Text, nullable=False, default=""),
            Column("script_output", Text, nullable=False, default=""),
            Column("job_id", Text, nullable=True),
            Column("sources", Text, nullable=False, default=""),
            Column("query_script", Text, nullable=False, default=""),
            Column("custom_column_types", JSON, nullable=True),
        ]

    @cached_property
    def _dataset_fields(self) -> list[str]:
        return [
            c.name  # type: ignore [attr-defined]
            for c in self._datasets_columns()
            if c.name  # type: ignore [attr-defined]
        ]

    @classmethod
    def _datasets_versions_columns(cls) -> list["SchemaItem"]:
        """Datasets versions table columns."""
        return [
            Column("id", Integer, primary_key=True),
            Column(
                "dataset_id",
                Integer,
                ForeignKey(f"{cls.DATASET_TABLE}.id", ondelete="CASCADE"),
                nullable=False,
            ),
            Column("version", Integer, nullable=False),
            # adding default for now until we fully remove shadow datasets
            Column("status", Integer, nullable=False, default=DatasetStatus.COMPLETE),
            Column("created_at", DateTime(timezone=True)),
            Column("finished_at", DateTime(timezone=True)),
            Column("error_message", Text, nullable=False, default=""),
            Column("error_stack", Text, nullable=False, default=""),
            Column("script_output", Text, nullable=False, default=""),
            Column("job_id", Text, nullable=True),
            Column("sources", Text, nullable=False, default=""),
            Column("query_script", Text, nullable=False, default=""),
            Column("custom_column_types", JSON, nullable=True),
            UniqueConstraint("dataset_id", "version"),
        ]

    @cached_property
    def _dataset_version_fields(self) -> list[str]:
        return [
            c.name  # type: ignore [attr-defined]
            for c in self._datasets_versions_columns()
            if c.name  # type: ignore [attr-defined]
        ]

    @classmethod
    def _datasets_dependencies_columns(cls) -> list["SchemaItem"]:
        """Datasets dependencies table columns."""
        return [
            Column("id", Integer, primary_key=True),
            # TODO remove when https://github.com/iterative/dvcx/issues/959 is done
            Column(
                "source_dataset_id",
                Integer,
                ForeignKey(f"{cls.DATASET_TABLE}.id"),
                nullable=False,
            ),
            Column(
                "source_dataset_version_id",
                Integer,
                ForeignKey(f"{cls.DATASET_VERSION_TABLE}.id"),
                nullable=True,
            ),
            # TODO remove when https://github.com/iterative/dvcx/issues/959 is done
            Column(
                "dataset_id",
                Integer,
                ForeignKey(f"{cls.DATASET_TABLE}.id"),
                nullable=True,
            ),
            Column(
                "dataset_version_id",
                Integer,
                ForeignKey(f"{cls.DATASET_VERSION_TABLE}.id"),
                nullable=True,
            ),
            # TODO remove when https://github.com/iterative/dvcx/issues/1121 is done
            # If we unify datasets and bucket listing then both bucket fields won't
            # be needed
            Column(
                "bucket_id",
                Integer,
                ForeignKey(f"{cls.STORAGE_TABLE}.id"),
                nullable=True,
            ),
            Column("bucket_version", Text, nullable=True),
        ]

    @classmethod
    def _storage_partial_columns(cls) -> list["SchemaItem"]:
        """Storage partial table columns."""
        return [
            Column("path_str", Text, nullable=False),
            # This is generated before insert and is not the SQLite rowid,
            # so it is not the primary key.
            Column("partial_id", Integer, nullable=False, index=True),
            Column("timestamp", DateTime(timezone=True)),
            Column("expires", DateTime(timezone=True)),
        ]

    def _get_storage_partial_table(self, name: str) -> Table:
        table = self.db.metadata.tables.get(name)
        if table is None:
            table = Table(
                name,
                self.db.metadata,
                *self._storage_partial_columns(),
            )
        return table

    #
    # Query Tables
    #

    def _partials_table(self, uri: StorageURI):
        return self._get_storage_partial_table(self._partials_table_name(uri))

    @cached_property
    def _storages(self) -> Table:
        return Table(self.STORAGE_TABLE, self.db.metadata, *self._buckets_columns())

    @cached_property
    def _partials(self) -> Table:
        assert (
            self._current_partials_table_name
        ), "Partials can only be used if uri/current_partials_table_name is set"
        return self._get_storage_partial_table(self._current_partials_table_name)

    @cached_property
    def _datasets(self) -> Table:
        return Table(self.DATASET_TABLE, self.db.metadata, *self._datasets_columns())

    @cached_property
    def _datasets_versions(self) -> Table:
        return Table(
            self.DATASET_VERSION_TABLE,
            self.db.metadata,
            *self._datasets_versions_columns(),
        )

    @cached_property
    def _datasets_dependencies(self) -> Table:
        return Table(
            self.DATASET_DEPENDENCY_TABLE,
            self.db.metadata,
            *self._datasets_dependencies_columns(),
        )

    #
    # Query Starters (These can be overridden by subclasses)
    #

    @abstractmethod
    def _storages_insert(self): ...

    def _storages_select(self, *columns):
        if not columns:
            return self._storages.select()
        return select(*columns).select_from(self._storages)

    def _storages_update(self):
        return self._storages.update()

    def _storages_delete(self):
        return self._storages.delete()

    @abstractmethod
    def _partials_insert(self): ...

    def _partials_select(self, *columns):
        if not columns:
            return self._partials.select()
        return select(*columns).select_from(self._partials)

    def _partials_update(self):
        return self._partials.update()

    @abstractmethod
    def _datasets_insert(self): ...

    def _datasets_select(self, *columns):
        if not columns:
            return self._datasets.select()
        return select(*columns).select_from(self._datasets)

    def _datasets_update(self):
        return self._datasets.update()

    def _datasets_delete(self):
        return self._datasets.delete()

    @abstractmethod
    def _datasets_versions_insert(self): ...

    def _datasets_versions_select(self, *columns):
        if not columns:
            return self._datasets_versions.select()
        return select(*columns).select_from(self._datasets_versions)

    def _datasets_versions_update(self):
        return self._datasets_versions.update()

    def _datasets_versions_delete(self):
        return self._datasets_versions.delete()

    @abstractmethod
    def _datasets_dependencies_insert(self): ...

    def _datasets_dependencies_select(self, *columns):
        if not columns:
            return self._datasets_dependencies.select()
        return select(*columns).select_from(self._datasets_dependencies)

    def _datasets_dependencies_update(self):
        return self._datasets_dependencies.update()

    def _datasets_dependencies_delete(self):
        return self._datasets_dependencies.delete()

    #
    # Table Name Internal Functions
    #

    def _partials_table_name(self, uri: StorageURI) -> str:
        sha = hashlib.sha256(uri.encode("utf-8")).hexdigest()[:12]
        return f"{self.PARTIALS_TABLE_NAME_PREFIX}_{sha}"

    @property
    def _current_partials_table_name(self) -> Optional[str]:
        if not self.uri:
            return None
        return self._partials_table_name(self.uri)

    #
    # Storages
    #

    def create_storage_if_not_registered(self, uri: StorageURI, conn=None) -> None:
        """Saves new storage if it doesn't exist in database."""
        self.db.execute(
            self._storages_insert()
            .values(
                uri=uri,
                status=StorageStatus.CREATED,
                error_message="",
                error_stack="",
            )
            .on_conflict_do_nothing(),
            conn=conn,
        )

    def register_storage_for_indexing(
        self,
        uri: StorageURI,
        force_update: bool = True,
        prefix: str = "",
    ) -> tuple[Storage, bool, bool, Optional[int]]:
        """
        Prepares storage for indexing operation.
        This method should be called before index operation is started
        It returns:
            - storage, prepared for indexing
            - boolean saying if indexing is needed
            - boolean saying if indexing is currently pending (running)
            - boolean saying if this storage is newly created
        """
        # This ensures that all calls to the DB are in a single transaction
        # and commit is automatically called once this function returns
        with self.db.transaction() as conn:
            # Create storage if it doesn't exist
            self.create_storage_if_not_registered(uri, conn=conn)
            storage = self.get_storage(uri, conn=conn)

            if storage.status == StorageStatus.PENDING:
                return storage, False, True, None

            if storage.is_expired or storage.status == StorageStatus.STALE:
                storage = self.mark_storage_pending(storage, conn=conn)
                return storage, True, False, None

            if (
                storage.status in (StorageStatus.PARTIAL, StorageStatus.COMPLETE)
                and not force_update
            ):
                partial_id = self.get_valid_partial_id(uri, prefix, raise_exc=False)
                if partial_id is not None:
                    return storage, False, False, partial_id
                return storage, True, False, None

            storage = self.mark_storage_pending(storage, conn=conn)
            return storage, True, False, None

    def find_stale_storages(self) -> None:
        """
        Finds all pending storages for which the last inserted node has happened
        before STALE_HOURS_LIMIT hours, and marks it as STALE.
        """
        s = self._storages
        with self.db.transaction() as conn:
            pending_storages = map(
                self.storage_class._make,
                self.db.execute(
                    self._storages_select().where(s.c.status == StorageStatus.PENDING),
                    conn=conn,
                ),
            )
            for storage in pending_storages:
                if storage.is_stale:
                    print(f"Marking storage {storage.uri} as stale")
                    self._mark_storage_stale(storage.id, conn=conn)

    def mark_storage_indexed(
        self,
        uri: StorageURI,
        status: int,
        ttl: int,
        end_time: Optional[datetime] = None,
        prefix: str = "",
        partial_id: int = 0,
        error_message: str = "",
        error_stack: str = "",
    ) -> None:
        """
        Marks storage as indexed.
        This method should be called when index operation is finished.
        """
        if status == StorageStatus.PARTIAL and not prefix:
            raise AssertionError("Partial indexing requires a prefix")

        if end_time is None:
            end_time = datetime.now(timezone.utc)
        expires = Storage.get_expiration_time(end_time, ttl)

        s = self._storages
        with self.db.transaction() as conn:
            self.db.execute(
                self._storages_update()
                .where(s.c.uri == uri)
                .values(  # type: ignore [attr-defined]
                    timestamp=end_time,
                    expires=expires,
                    status=status,
                    last_inserted_at=end_time,
                    error_message=error_message,
                    error_stack=error_stack,
                ),
                conn=conn,
            )

            if not self._current_partials_table_name:
                # This only occurs in tests
                return

            if status in (StorageStatus.PARTIAL, StorageStatus.COMPLETE):
                dir_prefix = posixpath.join(prefix, "")
                self.db.execute(
                    self._partials_insert().values(
                        path_str=dir_prefix,
                        timestamp=end_time,
                        expires=expires,
                        partial_id=partial_id,
                    ),
                    conn=conn,
                )

    def update_last_inserted_at(self, uri: Optional[StorageURI] = None) -> None:
        """Updates last inserted datetime in bucket with current time"""
        uri = uri or self.uri
        updates = {"last_inserted_at": datetime.now(timezone.utc)}
        s = self._storages
        self.db.execute(
            self._storages_update().where(s.c.uri == uri).values(**updates)  # type: ignore [attr-defined]
        )

    def get_all_storage_uris(self) -> Iterator[StorageURI]:
        """Returns all storage uris."""
        s = self._storages
        yield from (r[0] for r in self.db.execute(self._storages_select(s.c.uri)))

    def get_storage(self, uri: StorageURI, conn=None) -> Storage:
        """
        Gets storage representation from database.
        E.g. if s3 is used as storage this would be s3 bucket data
        """
        s = self._storages
        result = next(
            self.db.execute(self._storages_select().where(s.c.uri == uri), conn=conn),
            None,
        )
        if not result:
            raise StorageNotFoundError(f"Storage {uri} not found.")

        return self.storage_class._make(result)

    def list_storages(self) -> list[Storage]:
        result = self.db.execute(self._storages_select())
        if not result:
            return []

        return [self.storage_class._make(r) for r in result]

    def mark_storage_pending(self, storage: Storage, conn=None) -> Storage:
        # Update status to pending and dates
        updates = {
            "status": StorageStatus.PENDING,
            "timestamp": None,
            "expires": None,
            "last_inserted_at": None,
            "started_inserting_at": datetime.now(timezone.utc),
        }
        storage = storage._replace(**updates)  # type: ignore [arg-type]
        s = self._storages
        self.db.execute(
            self._storages_update().where(s.c.uri == storage.uri).values(**updates),  # type: ignore [attr-defined]
            conn=conn,
        )
        return storage

    def _mark_storage_stale(self, storage_id: int, conn=None) -> None:
        # Update status to pending and dates
        updates = {"status": StorageStatus.STALE, "timestamp": None, "expires": None}
        s = self._storages
        self.db.execute(
            self._storages.update().where(s.c.id == storage_id).values(**updates),  # type: ignore [attr-defined]
            conn=conn,
        )

    #
    # Partial Indexes
    #

    def init_partial_id(self, uri: StorageURI) -> None:
        """Initializes partial id for given storage."""
        if not uri:
            raise ValueError("uri for get_next_partial_id() cannot be empty")
        self.id_generator.init_id(f"partials:{uri}")

    def get_next_partial_id(self, uri: StorageURI) -> int:
        """Returns next partial id for given storage."""
        if not uri:
            raise ValueError("uri for get_next_partial_id() cannot be empty")
        return self.id_generator.get_next_id(f"partials:{uri}")

    def get_valid_partial_id(
        self, uri: StorageURI, prefix: str, raise_exc: bool = True
    ) -> Optional[int]:
        """Returns valid partial id for given storage."""
        # This SQL statement finds all entries that are
        # prefixes of the given prefix, matching this or parent directories
        # that are indexed.
        dir_prefix = posixpath.join(prefix, "")
        p = self._partials_table(uri)
        expire_values = self.db.execute(
            select(p.c.expires, p.c.partial_id)
            .select_from(p)
            .where(
                p.c.path_str == func.substr(dir_prefix, 1, func.length(p.c.path_str))
            )
            .order_by(p.c.expires.desc())
        )
        for expires, partial_id in expire_values:
            if not is_expired(expires):
                return partial_id
        if raise_exc:
            raise RuntimeError(f"Unable to get valid partial_id: {uri=}, {prefix=}")
        return None

    def get_last_partial_id(self, uri: StorageURI) -> Optional[int]:
        """Returns last partial id for given storage."""
        p = self._partials_table(uri)
        if not self.db.has_table(p.name):
            raise StorageNotFoundError(f"Storage {uri} partials are not found.")
        last_partial = self.db.execute(
            select(p.c.partial_id)
            .select_from(p)
            .order_by(p.c.timestamp.desc())
            .limit(1)
        )
        for (partial_id,) in last_partial:
            return partial_id
        return None

    #
    # Datasets
    #

    def create_dataset(
        self,
        name: str,
        status: int = DatasetStatus.CREATED,
        sources: Optional[list[str]] = None,
        query_script: str = "",
        custom_column_types: Optional[dict[str, Any]] = None,
        ignore_if_exists: bool = False,
        **kwargs,  # TODO registered = True / False
    ) -> DatasetRecord:
        """Creates new dataset."""
        column_types = {
            c.name: c.type.to_dict()
            for c in self.schema.dataset_row_cls.default_columns()
            if isinstance(c.type, SQLType)
        }
        if custom_column_types:
            column_types.update(custom_column_types)

        # TODO abstract this method and add registered = True based on kwargs
        query = self._datasets_insert().values(
            name=name,
            shadow=False,
            status=status,
            created_at=datetime.now(timezone.utc),
            error_message="",
            error_stack="",
            script_output="",
            sources="\n".join(sources) if sources else "",
            query_script=query_script,
            custom_column_types=json.dumps(column_types),
        )
        if ignore_if_exists:
            query = query.on_conflict_do_nothing(index_elements=["name"])
        self.db.execute(query)

        dataset = self.get_dataset(name)

        return dataset

    def create_dataset_version(
        self,
        dataset: DatasetRecord,
        version: int,
        status: int = DatasetStatus.CREATED,
        sources: str = "",
        query_script: str = "",
        error_message: str = "",
        error_stack: str = "",
        script_output: str = "",
        created_at: Optional[datetime] = None,
        finished_at: Optional[datetime] = None,
        custom_column_types: Optional[dict[str, Any]] = None,
        ignore_if_exists: bool = False,
        conn=None,
    ) -> DatasetRecord:
        """Creates new dataset version."""
        if status in [DatasetStatus.COMPLETE, DatasetStatus.FAILED]:
            finished_at = finished_at or datetime.now(timezone.utc)
        else:
            finished_at = None

        query = self._datasets_versions_insert().values(
            dataset_id=dataset.id,
            version=version,
            status=status,  # for now until we remove shadow datasets
            created_at=created_at or datetime.now(timezone.utc),
            finished_at=finished_at,
            error_message=error_message,
            error_stack=error_stack,
            script_output=script_output,
            sources=sources,
            query_script=query_script,
            custom_column_types=json.dumps(custom_column_types or {}),
        )
        if ignore_if_exists:
            query = query.on_conflict_do_nothing(
                index_elements=["dataset_id", "version"]
            )
        self.db.execute(query, conn=conn)

        return self.get_dataset(dataset.name, conn=conn)

    def remove_dataset(self, dataset: DatasetRecord) -> None:
        """Removes dataset."""
        d = self._datasets
        with self.db.transaction():
            self.remove_dataset_dependencies(dataset)
            self.remove_dataset_dependants(dataset)
            self.db.execute(self._datasets_delete().where(d.c.id == dataset.id))

    def update_dataset(
        self, dataset: DatasetRecord, conn=None, **kwargs
    ) -> DatasetRecord:
        """Updates dataset fields."""
        values = {}
        dataset_values = {}
        for field, value in kwargs.items():
            if field in self._dataset_fields[1:]:
                if field in ["labels", "custom_column_types"]:
                    values[field] = json.dumps(value) if value else None
                else:
                    values[field] = value
                if field == "custom_column_types":
                    dataset_values[field] = DatasetRecord.parse_custom_column_types(
                        value
                    )
                else:
                    dataset_values[field] = value

        if not values:
            # Nothing to update
            return dataset

        d = self._datasets
        self.db.execute(
            self._datasets_update().where(d.c.name == dataset.name).values(values),
            conn=conn,
        )  # type: ignore [attr-defined]

        result_ds = copy.deepcopy(dataset)
        result_ds.update(**dataset_values)
        return result_ds

    def update_dataset_version(
        self, dataset_version: DatasetVersion, conn=None, **kwargs
    ) -> DatasetVersion:
        """Updates dataset fields."""
        values = {}
        for field, value in kwargs.items():
            if field in self._dataset_version_fields[1:]:
                if field == "custom_column_types":
                    dataset_version.update(
                        **{field: DatasetRecord.parse_custom_column_types(value)}
                    )
                    values[field] = json.dumps(value) if value else None
                else:
                    values[field] = value
                    dataset_version.update(**{field: value})

        if not values:
            # Nothing to update
            return dataset_version

        dv = self._datasets_versions
        self.db.execute(
            self._datasets_versions_update()
            .where(dv.c.id == dataset_version.id)
            .values(values),
            conn=conn,
        )  # type: ignore [attr-defined]

        return dataset_version

    def _parse_dataset(self, rows) -> Optional[DatasetRecord]:
        versions = []
        for r in rows:
            versions.append(self.dataset_class.parse(*r))
        if not versions:
            return None
        return reduce(lambda ds, version: ds.merge_versions(version), versions)

    def remove_dataset_version(
        self, dataset: DatasetRecord, version: int
    ) -> DatasetRecord:
        """
        Deletes one single dataset version.
        If it was last version, it removes dataset completely
        """
        if not dataset.has_version(version):
            raise DatasetNotFoundError(
                f"Dataset {dataset.name} version {version} not found."
            )

        self.remove_dataset_dependencies(dataset, version)
        self.remove_dataset_dependants(dataset, version)

        d = self._datasets
        dv = self._datasets_versions
        self.db.execute(
            self._datasets_versions_delete().where(
                (dv.c.dataset_id == dataset.id) & (dv.c.version == version)
            )
        )

        if dataset.versions and len(dataset.versions) == 1:
            # had only one version, fully deleting dataset
            self.db.execute(self._datasets_delete().where(d.c.id == dataset.id))

        result_ds = copy.deepcopy(dataset)
        result_ds.remove_version(version)
        return result_ds

    def list_datasets(self) -> Iterator["DatasetRecord"]:
        """Lists all datasets."""
        d = self._datasets
        dv = self._datasets_versions
        query = self._datasets_select(
            *(getattr(d.c, f) for f in self._dataset_fields),
            *(getattr(dv.c, f) for f in self._dataset_version_fields),
        )
        j = d.join(dv, d.c.id == dv.c.dataset_id, isouter=True)

        query = query.select_from(j)
        rows = self.db.execute(query)

        for _, g in groupby(rows, lambda r: r[0]):
            dataset = self._parse_dataset(list(g))
            if dataset:
                dataset.sort_versions()
                yield dataset

    def get_dataset(self, name: str, conn=None) -> DatasetRecord:
        """Gets a single dataset by name"""
        d = self._datasets
        dv = self._datasets_versions
        query = self._datasets_select(
            *(getattr(d.c, f) for f in self._dataset_fields),
            *(getattr(dv.c, f) for f in self._dataset_version_fields),
        ).where(d.c.name == name)  # type: ignore [attr-defined]
        j = d.join(dv, d.c.id == dv.c.dataset_id, isouter=True)
        query = query.select_from(j)
        ds = self._parse_dataset(self.db.execute(query, conn=conn))
        if not ds:
            raise DatasetNotFoundError(f"Dataset {name} not found.")
        return ds

    def update_dataset_status(
        self,
        dataset: DatasetRecord,
        status: int,
        version: Optional[int] = None,
        error_message="",
        error_stack="",
        script_output="",
        conn=None,
    ) -> DatasetRecord:
        """
        Updates dataset status and appropriate fields related to status
        It also updates version if specified.
        """
        update_data: dict[str, Any] = {"status": status}
        if status in [DatasetStatus.COMPLETE, DatasetStatus.FAILED]:
            # if in final state, updating finished_at datetime
            update_data["finished_at"] = datetime.now(timezone.utc)
            if script_output:
                update_data["script_output"] = script_output

        if status == DatasetStatus.FAILED:
            update_data["error_message"] = error_message
            update_data["error_stack"] = error_stack

        self.update_dataset(dataset, conn=conn, **update_data)

        if version:
            dataset_version = dataset.get_version(version)
            self.update_dataset_version(dataset_version, conn=conn, **update_data)

        return dataset

    #
    # Dataset dependencies
    #

    def _insert_dataset_dependency(self, data: dict[str, Any]) -> None:
        """Method for inserting dependencies."""
        self.db.execute(self._datasets_dependencies_insert().values(**data))

    def add_storage_dependency(
        self,
        source_dataset_name: str,
        source_dataset_version: int,
        storage_uri: StorageURI,
        storage_timestamp_str: Optional[str] = None,
    ) -> None:
        source_dataset = self.get_dataset(source_dataset_name)
        storage = self.get_storage(storage_uri)

        self._insert_dataset_dependency(
            {
                "source_dataset_id": source_dataset.id,
                "source_dataset_version_id": (
                    source_dataset.get_version(source_dataset_version).id
                ),
                "bucket_id": storage.id,
                "bucket_version": storage_timestamp_str,
            }
        )

    def add_dataset_dependency(
        self,
        source_dataset_name: str,
        source_dataset_version: int,
        dataset_name: str,
        dataset_version: int,
    ) -> None:
        """Adds dataset dependency to dataset."""
        source_dataset = self.get_dataset(source_dataset_name)
        dataset = self.get_dataset(dataset_name)

        self._insert_dataset_dependency(
            {
                "source_dataset_id": source_dataset.id,
                "source_dataset_version_id": (
                    source_dataset.get_version(source_dataset_version).id
                ),
                "dataset_id": dataset.id,
                "dataset_version_id": dataset.get_version(dataset_version).id,
            }
        )

    def update_dataset_dependency_source(
        self,
        source_dataset: DatasetRecord,
        source_dataset_version: int,
        new_source_dataset: Optional[DatasetRecord] = None,
        new_source_dataset_version: Optional[int] = None,
    ) -> None:
        dd = self._datasets_dependencies

        if not new_source_dataset:
            new_source_dataset = source_dataset

        q = self._datasets_dependencies_update().where(
            dd.c.source_dataset_id == source_dataset.id
        )
        q = q.where(
            dd.c.source_dataset_version_id
            == source_dataset.get_version(source_dataset_version).id
        )

        data = {"source_dataset_id": new_source_dataset.id}
        if new_source_dataset_version:
            data["source_dataset_version_id"] = new_source_dataset.get_version(
                new_source_dataset_version
            ).id

        q = q.values(**data)
        self.db.execute(q)

    @abstractmethod
    def _dataset_dependencies_select_columns(self) -> list["SchemaItem"]:
        """
        Returns a list of columns to select in a query for fetching dataset dependencies
        """

    def get_direct_dataset_dependencies(
        self, dataset: DatasetRecord, version: int
    ) -> list[Optional[DatasetDependency]]:
        d = self._datasets
        dd = self._datasets_dependencies
        dv = self._datasets_versions
        s = self._storages

        dataset_version = dataset.get_version(version)

        select_cols = self._dataset_dependencies_select_columns()

        query = (
            self._datasets_dependencies_select(*select_cols)
            .where(
                (dd.c.source_dataset_id == dataset.id)
                & (dd.c.source_dataset_version_id == dataset_version.id)
            )
            .select_from(
                dd.join(d, dd.c.dataset_id == d.c.id, isouter=True)
                .join(s, dd.c.bucket_id == s.c.id, isouter=True)
                .join(dv, dd.c.dataset_version_id == dv.c.id, isouter=True)
            )
        )
        if version:
            dataset_version = dataset.get_version(version)
            query = query.where(dd.c.source_dataset_version_id == dataset_version.id)

        return [self.dependency_class.parse(*r) for r in self.db.execute(query)]

    def remove_dataset_dependencies(
        self, dataset: DatasetRecord, version: Optional[int] = None
    ) -> None:
        """
        When we remove dataset, we need to clean up it's dependencies as well
        """
        dd = self._datasets_dependencies

        q = self._datasets_dependencies_delete().where(
            dd.c.source_dataset_id == dataset.id
        )

        if version:
            q = q.where(
                dd.c.source_dataset_version_id == dataset.get_version(version).id
            )

        self.db.execute(q)

    def remove_dataset_dependants(
        self, dataset: DatasetRecord, version: Optional[int] = None
    ) -> None:
        """
        When we remove dataset, we need to clear its references in other dataset
        dependencies
        """
        dd = self._datasets_dependencies

        q = self._datasets_dependencies_update().where(dd.c.dataset_id == dataset.id)
        if version:
            q = q.where(dd.c.dataset_version_id == dataset.get_version(version).id)

        q = q.values(dataset_id=None, dataset_version_id=None)

        self.db.execute(q)
