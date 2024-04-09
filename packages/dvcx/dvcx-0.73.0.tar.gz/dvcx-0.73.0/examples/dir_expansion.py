"""
This script provides an example of the dir expansion query available
for datasets and storage indices. It prints the results, some summary
stats and verifies that the result is the same both for a dataset and
for a storage index with the same entries.
"""

import sys

import sqlalchemy as sa

from dvcx.catalog import get_catalog
from dvcx.error import DatasetNotFoundError
from dvcx.query import DatasetQuery

show_ids = False
if len(sys.argv) > 1:
    if sys.argv[1] == "--show-ids":
        show_ids = True
    else:
        raise RuntimeError(f"Invalid arg: {sys.argv[1]}")

source = "gcs://dvcx-datasets"
catalog = get_catalog(client_config={"aws_anon": True})
metastore = catalog.metastore
warehouse = catalog.warehouse

try:
    dataset = metastore.get_dataset("ds1")
except DatasetNotFoundError:
    DatasetQuery(source).save("ds1")
    dataset = metastore.get_dataset("ds1")

partial_id = metastore.get_valid_partial_id(source, "")
n = warehouse.nodes_table(source, partial_id)
dr = warehouse.dataset_rows(dataset, version=dataset.latest_version)


def get_values_to_compare(query):
    q = query.dir_expansion().subquery()
    return list(
        warehouse.db.execute(
            sa.select(
                q.c.source,
                q.c.parent,
                q.c.name,
                q.c.version,
                q.c.vtype,
                q.c.is_dir,
                q.c.location,
            )
        )
    )


dq = dr.dir_expansion()
result = warehouse.db.execute(dq)
for id_, vtype, is_dir, source, parent, name, version, _loc in result:
    id_str = f"{id_!r:12} " if show_ids else ""
    print(f"{id_str}{vtype!r:6} {version!r} {is_dir} {source!r} {parent!r} {name!r}")

print()
print("num dir expansion rows: ", len(list(warehouse.db.execute(dq))))
print(
    "num dir expansion files:",
    len(list(warehouse.db.execute(dq.having(~dq.selected_columns.is_dir)))),
)
print("num table rows:         ", len(list(warehouse.db.execute(dr.select()))))
print("same values:            ", get_values_to_compare(n) == get_values_to_compare(dr))
