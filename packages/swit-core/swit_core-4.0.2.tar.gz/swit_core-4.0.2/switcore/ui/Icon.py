from switcore.pydantic_base_model import SwitBaseModel


class Icon(SwitBaseModel):
    type: str
    image_url: str
    alt: str
