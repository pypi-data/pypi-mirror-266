from dvcx.query import C, DatasetQuery
from dvcx.sql.functions import path

source_path = "gcs://dvcx-zalando-hd-resized/zalando-hd-resized/"
ds = (
    DatasetQuery(source_path)
    .filter(C.name.glob("*.jpg"))
    .mutate(**{"class": path.name(C.parent), "label": path.name(path.parent(C.parent))})
)
