import pandas as pd
import pytest

from dvcx.lib.file import File
from dvcx.lib.webdataset_meta import MergeParquetAndNpz, WDSMetaError


def test_rows_order():
    pq_name = "111.parquet"
    npz_name = "123.npz"

    args = [File(name=pq_name), File(name=npz_name)]

    npz, pq = MergeParquetAndNpz.get_meta_streams(args)
    assert pq.name == pq_name
    assert npz.name == npz_name

    args.reverse()
    npz, pq = MergeParquetAndNpz.get_meta_streams(args)
    assert pq.name == pq_name
    assert npz.name == npz_name


def test_rows_num():
    with pytest.raises(WDSMetaError):
        MergeParquetAndNpz.get_meta_streams([File(name="111.parquet")])

    with pytest.raises(WDSMetaError):
        MergeParquetAndNpz.get_meta_streams(
            [
                File(name="111.parquet"),
                File(name="111.npz"),
                File(name="1111.parquet"),
            ]
        )


def test_content():
    df = pd.DataFrame(
        {
            "uid": ["12345", "67890", "abcde", "f0123"],
            "text": ["28", "22", "we", "hello world"],
        }
    )
    npz = {
        "b32_img": [[3.14] * 2] * 4,
        "b32_txt": [[2.72] * 2] * 4,
        "l14_img": [[1.41] * 2] * 4,
        "l14_txt": [[6.28] * 2] * 4,
        "dedup": [[2.3] * 2] * 4,
    }

    name = "111.parquet"
    stream = File(name=name)
    objs = list(MergeParquetAndNpz.parse_metafiles(npz, df, stream))

    assert len(objs) == 4

    file, meta = objs[0]
    assert file.name == "0"
    assert file.parent == name

    assert meta.b32_img == npz["b32_img"][0]
    assert meta.l14_img == npz["l14_img"][0]
