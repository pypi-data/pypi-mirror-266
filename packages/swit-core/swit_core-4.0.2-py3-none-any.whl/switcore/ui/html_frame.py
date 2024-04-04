from typing import Literal

from switcore.pydantic_base_model import SwitBaseModel


class HtmlFrame(SwitBaseModel):
    type: Literal['html_frame'] = 'html_frame'
    html_content: str
