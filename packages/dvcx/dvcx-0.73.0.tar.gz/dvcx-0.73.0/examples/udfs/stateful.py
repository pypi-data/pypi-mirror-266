"""
To install dependencies:

  pip install imgbeddings

"""

import uuid

from imgbeddings import imgbeddings

from dvcx.lib.param import Image
from dvcx.query import C, DatasetQuery, udf
from dvcx.sql.types import Array, Float32


@udf(
    params=(Image(),),
    output={"embedding": Array(Float32)},
    method="embedding",
)
class ImageEmbeddings:
    def __init__(self):
        self.emb = imgbeddings()

    def embedding(self, img):
        emb = self.emb.to_embeddings(img)
        return (emb[0].tolist(),)


if __name__ == "__main__":
    ds_name = uuid.uuid4().hex
    print(f"Saving to dataset: {ds_name}")
    # Save as a new dataset
    DatasetQuery(path="gcs://dvcx-datalakes/dogs-and-cats/").filter(
        C.name.glob("*cat*.jpg")
    ).limit(5).add_signals(ImageEmbeddings).save(ds_name)

    for row in DatasetQuery(name=ds_name).results()[:2]:
        print("default columns: ", row[:-1])
        print("embedding[:10]:  ", row[-1][:10])
        print(f"type: {type(row[-1]).__name__}, len: {len(row[-1])}")
        print()
