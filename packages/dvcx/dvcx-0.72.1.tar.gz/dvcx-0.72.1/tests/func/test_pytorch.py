import pytest
from torch import Size, Tensor
from torchvision.datasets import FakeData
from torchvision.transforms import v2

from dvcx.catalog import get_catalog
from dvcx.lib.param import Image
from dvcx.lib.pytorch import PytorchDataset
from dvcx.query import DatasetQuery, udf
from dvcx.sql.types import Int


@pytest.fixture
def fake_dataset(tmp_path):
    # Create fake images in labeled dirs
    data_path = tmp_path / "data"
    for i, (img, label) in enumerate(FakeData()):
        label = str(label)
        (data_path / label).mkdir(parents=True, exist_ok=True)
        img.save(data_path / label / f"{i}.jpg")

    # Create dataset from images
    uri = data_path.as_uri()
    catalog = get_catalog()
    catalog.add_storage(uri)

    @udf(params=("parent",), output={"label": Int})
    def extract_label(parent):
        return (int(parent),)

    yield DatasetQuery(uri).add_signals(extract_label).save("fake")

    catalog.remove_dataset("fake", version=1)
    catalog.id_generator.cleanup_for_tests()


def test_pytorch_dataset(tmp_path, fake_dataset):
    transform = v2.Resize((64, 64))
    pt_dataset = PytorchDataset(
        params=[Image(), "label"],
        name=fake_dataset.name,
        version=fake_dataset.version,
        transform=transform,
    )
    for img, label in pt_dataset:
        assert isinstance(img, Tensor)
        assert isinstance(label, int)
        assert img.size() == Size([3, 64, 64])
