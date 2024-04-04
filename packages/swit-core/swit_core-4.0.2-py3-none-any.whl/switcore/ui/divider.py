from typing import Literal

from switcore.pydantic_base_model import SwitBaseModel


class Divider(SwitBaseModel):
    type: Literal['divider'] = 'divider'