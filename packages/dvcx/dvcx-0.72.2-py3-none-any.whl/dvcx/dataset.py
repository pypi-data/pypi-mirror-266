import builtins
import json
from collections.abc import Iterable
from dataclasses import dataclass, fields
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    TypeVar,
)
from urllib.parse import urlparse

import attrs
from dateutil.parser import isoparse

from dvcx.sql.types import NAME_TYPES_MAPPING, SQLType

from .cache import UniqueId

if TYPE_CHECKING:
    from dvcx.storage import StorageURI

T = TypeVar("T", bound="DatasetRecord")
V = TypeVar("V", bound="DatasetVersion")
DD = TypeVar("DD", bound="DatasetDependency")

DATASET_PREFIX = "ds://"
QUERY_DATASET_NAME_PREFIX = "ds_query_"


def parse_dataset_uri(uri: str) -> tuple[str, Optional[int]]:
    """
    Parse dataser uri to extract name and version out of it (if version is defined)
    Example:
        Input: ds://zalando@v3
        Output: (zalando, 3)
    """
    p = urlparse(uri)
    if p.scheme != "ds":
        raise Exception("Dataset uri should start with ds://")
    s = p.netloc.split("@v")
    name = s[0]
    if len(s) == 1:
        return name, None
    if len(s) != 2:
        raise Exception(
            "Wrong dataset uri format, it should be: ds://<name>@v<version>"
        )
    version = int(s[1])
    return name, version


def create_dataset_uri(name: str, version: Optional[int] = None) -> str:
    """
    Creates a dataset uri based on dataset name and optionally version
    Example:
        Input: zalando, 3
        Output: ds//zalando@v3
    """
    uri = f"{DATASET_PREFIX}{name}"
    if version:
        uri += f"@v{version}"

    return uri


class DatasetDependencyType:
    DATASET = "dataset"
    STORAGE = "storage"


@dataclass
class DatasetDependency:
    id: int
    type: str
    name: str  # when the type is STORAGE, this is actually StorageURI
    version: str  # string until we'll have proper bucket listing versions
    created_at: datetime
    dependencies: list[Optional["DatasetDependency"]]

    @classmethod
    def parse(  # noqa: PLR0913
        cls: builtins.type[DD],
        id: int,
        dataset_id: Optional[int],
        dataset_version_id: Optional[int],
        bucket_id: Optional[int],
        bucket_version: Optional[str],
        dataset_name: Optional[str],
        dataset_created_at: Optional[datetime],
        dataset_version: Optional[int],
        dataset_version_created_at: Optional[datetime],
        bucket_uri: Optional["StorageURI"],
    ) -> Optional["DatasetDependency"]:
        if dataset_id:
            assert dataset_name is not None
            return cls(
                id,
                DatasetDependencyType.DATASET,
                dataset_name,
                (
                    str(dataset_version)  # type: ignore[arg-type]
                    if dataset_version
                    else None
                ),
                dataset_version_created_at or dataset_created_at,  # type: ignore[arg-type]
                [],
            )
        elif bucket_uri:
            return cls(
                id,
                DatasetDependencyType.STORAGE,
                bucket_uri,
                bucket_version,  # type: ignore[arg-type]
                isoparse(bucket_version),  # type: ignore[arg-type]
                [],
            )
        else:
            # dependency has been removed
            # TODO we should introduce flags for removed datasets, instead of
            # removing them from tables so that we can still have references
            return None

    @property
    def is_dataset(self) -> bool:
        return self.type == DatasetDependencyType.DATASET

    def __eq__(self, other):
        if not isinstance(other, DatasetDependency):
            return False

        return (
            self.type == other.type
            and self.name == other.name
            and self.version == other.version
        )

    def __hash__(self):
        return hash(f"{self.type}_{self.name}_{self.version}")


@dataclass
class DatasetStats:
    num_objects: int
    size: int  # in bytes


class Status:
    CREATED = 1
    PENDING = 2
    FAILED = 3
    COMPLETE = 4
    STALE = 6


@dataclass
class DatasetVersion:
    id: int
    dataset_id: int
    version: int
    status: int
    created_at: datetime
    finished_at: Optional[datetime]
    error_message: str
    error_stack: str
    script_output: str
    custom_column_types: dict[str, SQLType]
    job_id: Optional[str] = None
    sources: str = ""
    query_script: str = ""

    @classmethod
    def parse(
        cls: type[V],
        id: int,
        dataset_id: int,
        version: int,
        status: int,
        created_at: datetime,
        finished_at: Optional[datetime],
        error_message: str,
        error_stack: str,
        script_output: str,
        job_id: Optional[str],
        custom_column_types: dict[str, Any],
        sources: str = "",
        query_script: str = "",
    ):
        return cls(
            id,
            dataset_id,
            version,
            status,
            created_at,
            finished_at,
            error_message,
            error_stack,
            script_output,
            custom_column_types,
            job_id,
            sources,
            query_script,
        )

    def __eq__(self, other):
        if not isinstance(other, DatasetVersion):
            return False
        return self.version == other.version and self.dataset_id == other.dataset_id

    def __lt__(self, other):
        if not isinstance(other, DatasetVersion):
            return False
        return self.version < other.version

    def __hash__(self):
        return hash(f"{self.dataset_id}_{self.version}")

    def is_final_status(self) -> bool:
        return self.status in [Status.FAILED, Status.COMPLETE, Status.STALE]

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def custom_column_types_serialized(self) -> dict[str, Any]:
        if not self.custom_column_types:
            return {}

        return {
            c_name: c_type.to_dict()
            if isinstance(c_type, SQLType)
            else c_type().to_dict()
            for c_name, c_type in self.custom_column_types.items()
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DatasetVersion":
        kwargs = {f.name: d[f.name] for f in fields(cls) if f.name in d}
        return cls(**kwargs)


@dataclass
class DatasetRecord:
    id: int
    name: str
    description: Optional[str]
    labels: list[str]
    shadow: bool
    custom_column_types: dict[str, SQLType]
    versions: list[DatasetVersion]
    status: int = Status.CREATED
    created_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: str = ""
    error_stack: str = ""
    script_output: str = ""
    job_id: Optional[str] = None
    sources: str = ""
    query_script: str = ""

    @staticmethod
    def parse_custom_column_types(ct: dict[str, Any]) -> dict[str, SQLType]:
        return {
            c_name: NAME_TYPES_MAPPING[c_type["type"]].from_dict(c_type)  # type: ignore [attr-defined]
            for c_name, c_type in ct.items()
        }

    @classmethod
    def parse(  # noqa: PLR0913
        cls: type[T],
        id: int,
        name: str,
        description: Optional[str],
        labels: str,
        shadow: int,
        status: int,
        created_at: datetime,
        finished_at: Optional[datetime],
        error_message: str,
        error_stack: str,
        script_output: str,
        job_id: Optional[str],
        sources: str,
        query_script: str,
        custom_column_types: str,
        version_id: int,
        version_dataset_id: int,
        version: int,
        version_status: int,
        version_created_at: datetime,
        version_finished_at: Optional[datetime],
        version_error_message: str,
        version_error_stack: str,
        version_script_output: str,
        version_job_id: Optional[str],
        version_sources: Optional[str],
        version_query_script: Optional[str],
        version_custom_column_types: str,
    ) -> "DatasetRecord":
        labels_lst: list[str] = json.loads(labels) if labels else []
        custom_column_types_dct: dict[str, Any] = (
            json.loads(custom_column_types) if custom_column_types else {}
        )
        version_custom_column_types_dct: dict[str, str] = (
            json.loads(version_custom_column_types)
            if version_custom_column_types
            else {}
        )

        dataset_version = DatasetVersion.parse(
            version_id,
            version_dataset_id,
            version,
            version_status,
            version_created_at,
            version_finished_at,
            version_error_message,
            version_error_stack,
            version_script_output,
            version_job_id,
            cls.parse_custom_column_types(version_custom_column_types_dct),  # type: ignore[arg-type]
            version_sources,  # type: ignore[arg-type]
            version_query_script,  # type: ignore[arg-type]
        )

        return cls(
            id,
            name,
            description,
            labels_lst,
            bool(shadow),
            cls.parse_custom_column_types(custom_column_types_dct),  # type: ignore[arg-type]
            [dataset_version],
            status,
            created_at,
            finished_at,
            error_message,
            error_stack,
            script_output,
            job_id,
            sources,
            query_script,
        )

    @property
    def custom_column_types_serialized(self) -> dict[str, Any]:
        if not self.custom_column_types:
            return {}

        return {
            c_name: c_type.to_dict()
            if isinstance(c_type, SQLType)
            else c_type().to_dict()
            for c_name, c_type in self.custom_column_types.items()
        }

    def get_custom_column_types(self, version: int) -> dict[str, SQLType]:
        return (
            self.get_version(version).custom_column_types
            if version
            else self.custom_column_types
        )

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def merge_versions(self, other: "DatasetRecord") -> "DatasetRecord":
        """Merge versions from another dataset"""
        if other.id != self.id:
            raise RuntimeError("Cannot merge versions of datasets with different ids")
        if not other.versions:
            # nothing to merge
            return self
        if not self.versions:
            self.versions = []

        self.versions = list(set(self.versions + other.versions))
        return self

    def sort_versions(self, reverse=False) -> None:
        """Sorts versions by version number"""
        if not self.versions:
            return
        self.versions.sort(key=lambda v: v.version, reverse=reverse)

    def has_version(self, version: int) -> bool:
        return version in self.versions_values

    def is_valid_next_version(self, version: int) -> bool:
        """
        Checks if a number can be a valid next latest version for dataset.
        The only rule is that it cannot be lower than current latest version
        """
        if self.latest_version and self.latest_version >= version:
            return False
        return True

    def get_version(self, version: int) -> DatasetVersion:
        if not self.has_version(version):
            raise ValueError(f"Dataset {self.name} does not have version {version}")
        return next(
            v
            for v in self.versions  # type: ignore [union-attr]
            if v.version == version
        )

    def remove_version(self, version: int) -> None:
        if not self.versions or not self.has_version(version):
            return

        self.versions = [v for v in self.versions if v.version != version]

    def identifier(self, version: int) -> str:
        """
        Get identifier in the form my-dataset@v3
        """
        if not self.has_version(version):
            raise ValueError(f"Dataset {self.name} doesn't have a version {version}")
        return f"{self.name}@v{version}"

    def uri(self, version: int) -> str:
        """
        Dataset uri example: ds://dogs@v3
        """
        identifier = self.identifier(version)
        return f"{DATASET_PREFIX}{identifier}"

    @property
    def versions_values(self) -> list[int]:
        """
        Extracts actual versions from list of DatasetVersion objects
        in self.versions attribute
        """
        if not self.versions:
            return []

        return sorted(v.version for v in self.versions)

    @property
    def next_version(self) -> int:
        """Returns what should be next autoincrement version of dataset"""
        if not self.versions:
            return 1
        return max(self.versions_values) + 1

    @property
    def latest_version(self) -> int:
        """Returns latest version of a dataset"""
        return max(self.versions_values)

    @property
    def prev_version(self) -> Optional[int]:
        """Returns previous version of a dataset"""
        if len(self.versions) == 1:
            return None

        return sorted(self.versions_values)[-2]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DatasetRecord":
        versions = [DatasetVersion.from_dict(v) for v in d.pop("versions", [])]
        kwargs = {f.name: d[f.name] for f in fields(cls) if f.name in d}
        return cls(**kwargs, versions=versions)


@attrs.define
class DatasetRow:
    id: int
    vtype: str
    dir_type: int
    parent_id: Optional[int]
    parent: str
    name: str
    checksum: str
    etag: str
    version: str
    is_latest: bool
    last_modified: Optional[datetime]
    size: int
    owner_name: str
    owner_id: str
    anno: Optional[str]
    random: int
    location: Optional[str]
    source: "StorageURI"
    custom: Optional[dict] = attrs.field(factory=dict)

    @property
    def path(self) -> str:
        return f"{self.parent}/{self.name}" if self.parent else self.name

    @classmethod
    def from_result_row(cls, columns: list[str], values: Iterable[Any]) -> "DatasetRow":
        row = dict(zip(columns, values))
        return cls.from_dict(row)

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "DatasetRow":
        core_fields = {key: value for (key, value) in row.items() if hasattr(cls, key)}
        custom_fields = {
            key: value for (key, value) in row.items() if key not in core_fields
        }
        return cls(**core_fields, custom=custom_fields)

    def for_insert(self) -> dict[str, Any]:
        """Prepares data for insert"""
        d = attrs.asdict(self)
        del d["id"]  # id will be autogenerated in DB
        del d["parent_id"]  # parent_id is deprecated
        d.update(d.pop("custom", {}))
        return d

    def __getitem__(self, col):
        if hasattr(self, col):
            return getattr(self, col)
        elif self.custom and col in self.custom:
            return self.custom[col]
        raise KeyError

    def as_uid(self) -> UniqueId:
        return UniqueId(
            self.source,
            self.parent,
            self.name,
            self.etag,
            self.size,
            self.vtype,
            self.location,
        )
