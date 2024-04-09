from typing import Optional

import numpy as np
from pydantic import Field

from dvcx.lib.feature import Feature
from dvcx.lib.feature_udf import FeatureAggregator
from dvcx.lib.file import File, FileInfo
from dvcx.lib.utils import DvcxError
from dvcx.query import C
from dvcx.sql.functions import path

try:
    import pandas as pd
except ImportError:
    pd = None


class WDSMetaError(DvcxError):
    def __init__(self, msg):
        super().__init__(msg)


def parse_wds_meta(ds):
    return ds.aggregate(MergeParquetAndNpz(), partition_by=path.file_stem(C.name))


class LaionMeta(Feature):
    uid: str = Field(default="")
    url: str = Field(default="")
    text: str = Field(default="")
    original_width: int = Field(default=-1)
    original_height: int = Field(default=-1)
    clip_b32_similarity_score: float = Field(default=0.0)
    clip_l14_similarity_score: float = Field(default=0.0)
    face_bboxes: Optional[list[list[float]]] = Field(default=None)
    sha256: str = Field(default="")

    b32_img: list[float] = Field(default=None)
    b32_txt: list[float] = Field(default=None)
    l14_img: list[float] = Field(default=None)
    l14_txt: list[float] = Field(default=None)
    dedup: list[float] = Field(default=None)


class MergeParquetAndNpz(FeatureAggregator):
    def __init__(self):
        super().__init__(File, [FileInfo, LaionMeta])

    def process(self, args):
        stream_npz, stream_pq = self.get_meta_streams(args)

        with stream_pq.open() as fd_pq, stream_npz.open() as fd_npz:
            df = pd.read_parquet(fd_pq)
            npz_file = np.load(fd_npz)

            yield from self.parse_metafiles(npz_file, df, stream_pq)

    @staticmethod
    def get_meta_streams(args):
        if len(args) != 2:
            filenames = " ".join([f.get_full_path() for f in args])
            raise WDSMetaError(f"npz-parquet pair mismatch: {filenames}")
        stream_pq = args[0]
        stream_npz = args[1]
        if args[0].get_file_ext() != "parquet":
            stream_pq, stream_npz = stream_npz, stream_pq
        return stream_npz, stream_pq

    @staticmethod
    def parse_metafiles(npz_file, df, stream_pq):
        b32_img = npz_file["b32_img"]
        b32_txt = npz_file["b32_txt"]
        l14_img = npz_file["l14_img"]
        l14_txt = npz_file["l14_txt"]
        dedup = npz_file["dedup"]
        for idx, (_, row) in enumerate(df.iterrows()):
            if idx > 1000:
                break

            fstream = FileInfo(
                name=str(idx),
                source=stream_pq.source,
                parent=f"{stream_pq.get_full_name()}",
                version=stream_pq.version,
                etag=f"{stream_pq.etag}_{stream_pq.etag}",
                vtype="parquet",
            )

            pq_dict = row.to_dict()
            npz_dict = {
                "b32_img": b32_img[idx],
                "b32_txt": b32_txt[idx],
                "l14_img": l14_img[idx],
                "l14_txt": l14_txt[idx],
                "dedup": dedup[idx],
            }

            yield fstream, LaionMeta(**(pq_dict | npz_dict))
