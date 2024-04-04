from enum import Enum
from typing import Literal

from pydantic import model_validator

from switcore.pydantic_base_model import SwitBaseModel


class TextParagraphColorTypes(str, Enum):
    gray900 = "gray900"
    gray800 = "gray800"
    gray700 = "gray700"


class TextParagraphSizeTypes(str, Enum):
    medium = "medium"
    large = "large"


class TextParagraphStyle(SwitBaseModel):
    # TODO : TextParagraphStyle 스펙 확인 필요
    bold: bool = False
    color: TextParagraphColorTypes = TextParagraphColorTypes.gray900
    size: TextParagraphSizeTypes = TextParagraphSizeTypes.medium
    max_lines: int = 0

    @model_validator(mode='after')
    def check_max_lines(self):
        if self.max_lines < 0 or self.max_lines > 2:
            raise ValueError('max_lines must be between 0 and 2 inclusive.')
        return self


class TextParagraph(SwitBaseModel):
    type: Literal['text'] = 'text'
    markdown: bool = False
    content: str
    style: TextParagraphStyle | None = None
