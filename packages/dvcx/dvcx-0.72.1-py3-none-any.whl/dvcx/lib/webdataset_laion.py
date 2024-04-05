from typing import Optional

from pydantic import Field

from dvcx.lib.webdataset import WDSBasic, WDSReadableSubclass


class Laion(WDSReadableSubclass):
    uid: str = Field(default="")
    face_bboxes: Optional[list[list[float]]] = Field(default=None)
    caption: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    key: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    original_width: Optional[int] = Field(default=None)
    original_height: Optional[int] = Field(default=None)
    exif: Optional[str] = Field(default=None)
    sha256: Optional[str] = Field(default=None)

    @staticmethod
    def _reader(builder, item):
        return Laion.model_validate_json(builder.read_text(item))


class WDSLaion(WDSBasic):
    txt: Optional[str] = Field(default=None)
    json: Laion  # type: ignore
