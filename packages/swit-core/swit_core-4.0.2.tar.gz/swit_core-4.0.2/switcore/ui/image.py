from typing import Literal

from switcore.pydantic_base_model import SwitBaseModel


class Image(SwitBaseModel):
    type: Literal['image'] = 'image'
    image_url: str
    alt: str | None = None
    style: dict | None = None
