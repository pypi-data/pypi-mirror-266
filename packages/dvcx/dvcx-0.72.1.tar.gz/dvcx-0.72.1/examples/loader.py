"""
A simple data loader example.

This downloads and displays the first 5 images of the dataset.
"""

from contextlib import closing

from dvcx.catalog import get_catalog
from dvcx.error import DatasetNotFoundError
from dvcx.lib.param import Image
from dvcx.query import C, DatasetQuery

catalog = get_catalog()
try:
    ds = catalog.get_dataset("cats")
except DatasetNotFoundError:
    ds = (
        DatasetQuery(
            path="gcs://dvcx-datalakes/dogs-and-cats/",
            catalog=catalog,
        )
        .filter(C.name.glob("*cat*.jpg"))
        .save("cats")
    )


images = ds.limit(5).extract(Image(), cache=False)
with closing(images):
    for (img,) in images:
        img.show()
