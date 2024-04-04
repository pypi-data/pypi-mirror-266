from switcore.pydantic_base_model import SwitBaseModel
from switcore.ui.text_paragraph import TextParagraph


class Item(SwitBaseModel):
    label: str
    text: TextParagraph
