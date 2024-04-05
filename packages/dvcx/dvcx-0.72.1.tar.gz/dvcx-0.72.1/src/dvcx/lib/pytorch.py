import logging
from typing import TYPE_CHECKING, Any, Optional

from torch import float32
from torch.distributed import get_rank, get_world_size
from torch.utils.data import IterableDataset, get_worker_info

from dvcx.asyn import ASYNC_WORKERS
from dvcx.query import DatasetQuery

if TYPE_CHECKING:
    from dvcx.query.schema import UDFParamSpec


logger = logging.getLogger("dvcx")


class PytorchDataset(IterableDataset):
    def __init__(
        self,
        params: "UDFParamSpec",
        name: str,
        version: Optional[int] = None,
        transform: Any = None,
        workers: int = ASYNC_WORKERS,
        cache: bool = False,
    ):
        """
        Pytorch IterableDataset that streams DVCx datasets.

        Args:
            params (UDFParamSpec): Fields from DVCx dataset to stream.
            name (str): Name of DVCx dataset to stream.
            version (int): Version of DVCx dataset to stream.
            transform (Any): Pytorch v2 transforms to apply to the dataset.
            workers (int): Number of async workers per process.
            cache (bool): Whether to download and cache objects locally.
        """
        self.params = params
        self.name = name
        self.version = version
        self.transform = transform
        self.workers = workers
        self.cache = cache

    def __iter__(self):
        total_rank, total_workers = self.get_rank_and_workers()
        q = DatasetQuery(name=self.name, version=self.version).chunk(
            total_rank, total_workers
        )
        stream = q.extract(*self.params, workers=self.workers, cache=self.cache)
        for row in stream:
            # Auto convert types
            row = self.image_to_tensor(row)
            # Apply transforms
            if self.transform:
                row = self.transform(row)
            yield row

    @staticmethod
    def get_rank_and_workers() -> tuple[int, int]:
        """Get combined rank and number of workers across all nodes."""
        try:
            world_rank = get_rank()
            world_size = get_world_size()
        except ValueError:
            world_rank = 0
            world_size = 1
        worker_info = get_worker_info()
        if worker_info:
            worker_rank = worker_info.id
            num_workers = worker_info.num_workers
        else:
            worker_rank = 0
            num_workers = 1
        total_workers = world_size * num_workers
        total_rank = world_rank * num_workers + worker_rank
        return total_rank, total_workers

    @staticmethod
    def image_to_tensor(data: tuple[Any]) -> tuple[Any]:
        """Convert image data to tensor."""
        try:
            from torchvision.transforms import v2
        except ImportError:
            logger.warning(
                "Skipping image conversion due to missing dependency torchvision."
            )
            return data
        to_tensor = v2.Compose([v2.ToImage(), v2.ToDtype(float32, scale=True)])
        return to_tensor(data)
