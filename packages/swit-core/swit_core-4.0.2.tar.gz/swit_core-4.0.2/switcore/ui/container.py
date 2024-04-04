from typing import Literal

from pydantic import Field

from switcore.pydantic_base_model import SwitBaseModel
from switcore.ui.button import Button
from switcore.ui.datepicker import DatePicker
from switcore.ui.select import Select


class Container(SwitBaseModel):
    type: Literal['container'] = 'container'
    elements: list[Select | Button | DatePicker] = Field(discriminator='resource_type')

