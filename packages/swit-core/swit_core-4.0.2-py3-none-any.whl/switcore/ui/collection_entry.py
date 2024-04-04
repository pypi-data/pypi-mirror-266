from typing import Literal
from enum import Enum

from pydantic import Field

from switcore.pydantic_base_model import SwitBaseModel
from switcore.ui.element_components import SubText, Tag, StaticAction
from switcore.ui.image import Image
from switcore.ui.text_paragraph import TextParagraph


class TextStyle(SwitBaseModel):
    bold: bool = False
    color: str
    size: str
    max_lines: int


class Background(SwitBaseModel):
    color: Literal['none', 'lightblue'] = 'none'


class MetadataItem(SwitBaseModel):
    type: str
    content: str | None = None
    style: dict | None = None
    image_url: str | None = None


class TextSection(SwitBaseModel):
    text: TextParagraph
    metadata_items: list[SubText | Image | Tag] = Field(default_factory=list, discriminator='type', max_length=4)


class CollectionEntry(SwitBaseModel):
    type: Literal['collection_entry'] = 'collection_entry'
    start_section: Image | None = None
    text_sections: list[TextSection]
    vertical_alignment: Literal['top', 'middle', 'bottom'] = 'top'
    background: Background | None = None
    action_id: str | None = None
    static_action: StaticAction | None = None
    draggable: bool = False
