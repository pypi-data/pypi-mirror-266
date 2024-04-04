from enum import Enum
from typing import Literal

from pydantic import validator, model_validator, Field

from switcore.pydantic_base_model import SwitBaseModel
from switcore.ui.element_components import Tag
from switcore.ui.image import Image
from switcore.ui.select_item import SelectItem


class NoOptionsReason(SwitBaseModel):
    message: str


class Option(SelectItem):
    """
        https://devdocs.swit.io/docs/user-actions/ref/schemas/select
    """
    icon: Image | None = None
    tag: Tag | None = None


class OptionGroup(SwitBaseModel):
    label: str
    options: list[Option] = Field(default_factory=list, min_items=1)


class SelectStyleTypes(str, Enum):
    filled = "filled"
    outlined = "outlined"
    ghost = "ghost"


class Style(SwitBaseModel):
    variant: SelectStyleTypes = SelectStyleTypes.outlined


class SelectQuery(SwitBaseModel):
    query_server: bool = True
    disabled: bool = False
    placeholder: str | None = None
    value: str | None = None
    action_id: str | None = None


class Select(SwitBaseModel):
    type: Literal['select'] = 'select'
    placeholder: str | None = None
    multiselect: bool = False
    trigger_on_input: bool = False
    value: list[str] | None = None
    options: list[Option] = []
    option_groups: list[OptionGroup] = []
    no_options_reason: NoOptionsReason | None = None
    style: Style | None = None
    query: SelectQuery | None = None

    @model_validator(mode='after')
    def validate_options_exclusivity(self):
        if len(self.options) > 0 and len(self.option_groups) > 0:
            raise ValueError("Only one of 'options' or 'option_groups' should be provided.")
        return self
