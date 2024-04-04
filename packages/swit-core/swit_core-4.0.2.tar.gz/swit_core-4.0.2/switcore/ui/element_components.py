from typing import Any, Literal

from pydantic import model_validator

from switcore.pydantic_base_model import SwitBaseModel


class TagStyle(SwitBaseModel):
    color: Literal['primary', 'secondary', 'danger'] = 'secondary'
    shape: Literal['rectangular', 'rounded'] = 'rectangular'

    class Config:
        use_enum_values = True

    @model_validator(mode='before')
    @classmethod
    def check_color_and_shape(cls, values: dict[str, Any]) -> dict[str, Any]:
        color: str | None = values.get('color')
        shape: str | None = values.get('shape')
        if color is None and shape is None:
            raise ValueError("color and shape cannot be None at the same time")
        return values


class Tag(SwitBaseModel):
    type: str = "tag"
    content: str
    style: TagStyle | None = None


class SubText(SwitBaseModel):
    type: str = "subtext"
    content: str


class OpenOauthPopup(SwitBaseModel):
    action_type: str = "open_oauth_popup"
    link_url: str


class OpenLink(SwitBaseModel):
    action_type: str = "open_link"
    link_url: str


class CloseView(SwitBaseModel):
    action_type: str = "close_view"


class WriteToClipboard(SwitBaseModel):
    action_type: str = "write_to_clipboard"
    content: str


StaticAction = OpenOauthPopup | OpenLink | WriteToClipboard | CloseView
