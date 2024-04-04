from typing import Literal

from switcore.pydantic_base_model import SwitBaseModel
from switcore.ui.element_components import StaticAction


class InteractiveImage(SwitBaseModel):
    type: Literal['interactive_image'] = 'interactive_image'
    image_url: str
    alt: str | None = None
    action_id: str | None = None
    static_action: StaticAction | None = None
    draggable: bool = False
