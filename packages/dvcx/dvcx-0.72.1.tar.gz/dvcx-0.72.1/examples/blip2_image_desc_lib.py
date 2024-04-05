# pip install torch
import torch

from dvcx.lib.hf_image_to_text import BLIP2describe
from dvcx.query import C, DatasetQuery

source = "gcs://dvcx-datalakes/dogs-and-cats/"

if torch.backends.mps.is_available():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"


if __name__ == "__main__":
    results = (
        DatasetQuery(
            source,
            client_config={"aws_anon": True},
        )
        .filter(C.name.glob("cat*.jpg"))
        .limit(5)
        .add_signals(
            BLIP2describe(
                # device=device,
                device="cpu",
            ),
            parallel=False,
        )
        .select("source", "parent", "name", "description", "error")
        .results()
    )
    print(*results, sep="\n")
