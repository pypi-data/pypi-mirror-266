from typing import TYPE_CHECKING

import attrs

from dvcx.query.schema import Object, UDFParameter

if TYPE_CHECKING:
    from dvcx.catalog import Catalog
    from dvcx.dataset import DatasetRow as Row


def Image(formats=None, mode="RGB", size=None, transform=None):  # noqa: N802
    try:
        import PIL.Image
    except ImportError as exc:
        raise ImportError(
            "Missing dependency Pillow for computer vision:\n"
            "To install run:\n\n"
            "  pip install 'dvcx[cv]'\n"
        ) from exc

    def load_img(raw):
        img = PIL.Image.open(raw, formats=formats).convert(mode)
        if size:
            img = img.resize(size)
        if transform:
            img = transform(img)
        return img

    return Object(load_img)


@attrs.define(slots=False)
class Label(UDFParameter):
    """
    Encode column value as an index into the provided list of labels.
    """

    column: str
    classes: list

    def get_value(self, catalog: "Catalog", row: "Row", **kwargs) -> int:
        label = row[self.column]
        return self.classes.index(label)
